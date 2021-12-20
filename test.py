import asyncio

from Application.database import DBSessionPool


async def main():
    with DBSessionPool.get_instance() as conn:
        with conn.cursor() as cur:
            sql = '''
            SELECT SESSION_ID, RTRIM(USER_ID), RTRIM(IP_ADDRESS), USER_AGENT, CREATION_TIME 
            FROM "Session" 
            WHERE SESSION_ID = :s_id'''

            cur.execute(sql, s_id="b08267d2-870f-4dac-b4fa-2642bc566403")

            result = cur.fetchone()


# with DBSessionPool.get_instance() as conn:
#     with conn.cursor() as cur:
#         res = cur.callfunc("register", int, ['test', 'test', 'test', 'test'])
#         fetches = cur.execute('''SELECT * FROM "User"''').fetchall()
#         print(res)
#         print(fetches)
#     conn.commit()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
