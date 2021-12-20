import time
import uuid
from typing import Dict, Optional

from .database import DBSessionPool
from .model import Session


class SessionManager:
    cache: Dict[str, Session]

    def __init__(self):
        self.cache = dict()

    async def create_session(self, user_id: str, ip_addr: str, user_agent: str) -> Session:
        with DBSessionPool.get_instance() as conn:
            with conn.cursor() as cur:
                sql = '''
                     MERGE INTO "Session"
                     USING DUAL
                         ON (USER_ID = RPAD(:u_id, 12))
                     WHEN MATCHED THEN
                         UPDATE SET
                             SESSION_ID = :s_id,
                             IP_ADDRESS = :ip_addr,
                             USER_AGENT = :agent,
                             CREATION_TIME = SYSDATE
                     WHEN NOT MATCHED THEN
                         INSERT (SESSION_ID, USER_ID, IP_ADDRESS, USER_AGENT, CREATION_TIME)
                             VALUES (:s_id, :u_id, :ip_addr, :agent, SYSDATE)'''

                new_session_id = str(uuid.uuid4())

                cur.execute(sql, s_id=new_session_id, u_id=user_id, ip_addr=ip_addr, agent=user_agent)
            conn.commit()

        session = Session(
            session_id=new_session_id,
            user_id=user_id,
            ip_address=ip_addr,
            user_agent=user_agent,
            last_modified=time.time())

        self.cache[new_session_id] = session
        return session

    async def delete_expired(self, seconds: int):
        expired = [(sid,) for sid, session in self.cache.items() if session.last_modified < time.time() - seconds]

        list(map(self.cache.pop, expired))

        with DBSessionPool.get_instance() as conn:
            with conn.cursor() as cur:
                sql = '''
                DELETE FROM "Session"
                WHERE SESSION_ID = :s_id
                '''

                cur.executemany(sql, expired)
            conn.commit()

    async def delete(self, session_id: str):
        self.cache.pop(session_id)

        with DBSessionPool.get_instance() as conn:
            with conn.cursor() as cur:
                sql = '''
                DELETE FROM "Session"
                WHERE SESSION_ID = :s_id
                '''

                cur.execute(sql, s_id=session_id)
            conn.commit()

    async def update_session(self, session_id: str):
        if session_id in self.cache:
            self.cache.get(session_id).last_modified = time.time()

    async def get_session(self, session_id: str) -> Optional[Session]:
        if session_id in self.cache:
            return self.cache.get(session_id)
        else:
            return await self.get_session_from_db(session_id)

    async def get_session_from_db(self, session_id: str) -> Optional[Session]:
        with DBSessionPool.get_instance() as conn:
            with conn.cursor() as cur:
                sql = '''
                SELECT SESSION_ID, RTRIM(USER_ID), RTRIM(IP_ADDRESS), USER_AGENT, CREATION_TIME 
                FROM "Session" 
                WHERE SESSION_ID = :s_id'''

                cur.execute(sql, s_id=session_id)

                result = cur.fetchone()

        if not result:
            return None

        session = Session(
            session_id=result[0],
            user_id=result[1],
            ip_address=result[2],
            user_agent=result[3],
            last_modified=result[4].timestamp())

        self.cache[session_id] = session
        return session
