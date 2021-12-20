from fastapi import Cookie

from ..container import RouteContainer
from ..database import DBSessionPool


class StockRoute(RouteContainer):
    def route(self):
        @self.app.get("/stock/my-stock")
        async def my_stock(session_id: str = Cookie(None)):
            session = await self.session_manager.get_session(session_id)

            with DBSessionPool.get_instance() as conn:
                with conn.cursor() as cur:
                    sql = '''
                    SELECT RTRIM(SH.STOCK_ID), RTRIM(S.STOCK_NAME), SH.AVG_PRICE, SH.QUANTITY
                    FROM "Stock_Has" SH, "Stock" S 
                    WHERE USER_ID = RPAD(:user_id, 12) AND SH.STOCK_ID = S.STOCK_ID
                    '''
                    cur.execute(sql, user_id=session.user_id)
                    result = cur.fetchall()

                await self.session_manager.update_session(session_id)

                return result

        @self.app.get("/stock/add-stock")
        async def add_stock(stock_id: str, price: int, quantity: int, session_id: str = Cookie(None)):
            session = await self.session_manager.get_session(session_id)

            with DBSessionPool.get_instance() as conn:
                with conn.cursor() as cur:
                    sql = '''
                    SELECT AVG_PRICE, QUANTITY
                    FROM "Stock_Has" 
                    WHERE USER_ID = RPAD(:user_id, 12) AND STOCK_ID = RPAD(:stock_id, 12)
                    '''
                    cur.execute(sql, user_id=session.user_id, stock_id=stock_id)
                    result = cur.fetchone()

                if result:
                    avg_price, qty = result
                    avg_price = ((avg_price * qty) + (price * quantity)) / (qty + quantity)
                    qty = qty + quantity
                else:
                    avg_price = price
                    qty = quantity

                with conn.cursor() as cur:
                    sql = '''
                         MERGE INTO "Stock_Has"
                         USING DUAL
                             ON (USER_ID = RPAD(:user_id, 12) AND STOCK_ID = RPAD(:stock_id, 12))
                         WHEN MATCHED THEN
                             UPDATE SET
                                 AVG_PRICE = :avg_price,
                                 QUANTITY = :quantity
                         WHEN NOT MATCHED THEN
                             INSERT (STOCK_ID, USER_ID, AVG_PRICE, QUANTITY)
                                 VALUES (:stock_id, :user_id, :avg_price, :quantity)'''

                    cur.execute(sql, user_id=session.user_id, stock_id=stock_id, avg_price=avg_price, quantity=qty)
                conn.commit()

            await self.session_manager.update_session(session_id)

            return
