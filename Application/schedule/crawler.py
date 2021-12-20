import asyncio

from ..database import DBSessionPool
from ..finance import NAVER
from ..scheduler import JobContainer


class CrawlingJob(JobContainer):

    def jobs(self):
        @self.scheduler.scheduled_job('cron', day_of_week="1-5", hour="18", minute="0", id="daily_crawling")
        async def daily_crawling():
            with DBSessionPool.get_instance() as conn:
                with conn.cursor() as cur:
                    cur.execute('SELECT TRIM(STOCK_ID) FROM "Stock"')
                    codes = list(zip(*cur))[0]

                result = await asyncio.gather(*[NAVER.get_price_per_day(code, 1) for code in codes])

                price = map(lambda x: x.get('data')[0], result)
                price = map(lambda x: [x[0], *map(lambda y: float(NAVER.REGEX_1.sub('', y)), x[1:2] + x[3:])], price)

                rows = [(x, *y) for x, y in zip(codes, price)]

                sql = '''
                     MERGE INTO "Stock_History"
                     USING DUAL
                         ON (STOCK_ID = RPAD(:stock_id, 12) AND "DATE" = TO_DATE(:today, 'YYYY.MM.DD'))
                     WHEN MATCHED THEN
                         UPDATE SET
                             CLOSING_PRICE = :closing,
                             STARTING_PRICE =  :starting,
                             HIGH_PRICE = :high,
                             LOW_PRICE = :low,
                             VOLUME = :volume
                     WHEN NOT MATCHED THEN
                         INSERT (STOCK_ID, "DATE", CLOSING_PRICE, STARTING_PRICE, HIGH_PRICE, LOW_PRICE, VOLUME)
                             VALUES (:stock_id, TO_DATE(:today,'YYYY.MM.DD'), :closing, :starting, :high, :low, :volume)'''

                with conn.cursor() as cur:
                    cur.executemany(sql, rows)
                conn.commit()

        @self.scheduler.scheduled_job('cron', minute='*/1', id="current_state_update")
        async def state_update():
            with DBSessionPool.get_instance() as conn:
                with conn.cursor() as cur:
                    sql = '''SELECT TRIM(STOCK_ID) FROM "Stock"'''
                    cur.execute(sql)
                    codes = list(zip(*cur))[0]

                result = await asyncio.gather(*[NAVER.get_price_per_time(code, 1) for code in codes])
                price = map(lambda x: x.get('data')[0][1], result)
                price = tuple(map(lambda x: NAVER.REGEX_1.sub('', x), price))

                rows = list(zip(codes, price))

                sql = '''
                MERGE INTO "Stock_Current"
                USING DUAL
                    ON (STOCK_ID = RPAD(:stock_id, 12))
                WHEN MATCHED THEN
                    UPDATE SET
                        "DATE" = SYSDATE,
                        PRICE = :price
                WHEN NOT MATCHED THEN
                    INSERT (STOCK_ID, "DATE", PRICE)
                        VALUES (:stock_id, SYSDATE, :price)'''

                with conn.cursor() as cur:
                    cur.executemany(sql, rows)
                conn.commit()

                await asyncio.gather(
                    *[self.push_event_manager.push(f"price_{code}", price=price) for code, price in rows]
                )
