from __future__ import annotations

import cx_Oracle

from . import config

__all__ = (
    "DBSessionPool",
)

_CONFIG = config.get_config()

DB_HOST = _CONFIG.get("database.host")
DB_ID = _CONFIG.get("database.id")
DB_PW = _CONFIG.get("database.password")
DB_ENCODING = _CONFIG.get("database.encoding")

DB_POOL_MIN = _CONFIG.get("database.pool.min")
DB_POOL_MAX = _CONFIG.get("database.pool.max")
DB_POOL_INC = _CONFIG.get("database.pool.increment")

_pool = cx_Oracle.SessionPool(
    DB_ID, DB_PW, DB_HOST,
    min=DB_POOL_MIN,
    max=DB_POOL_MAX,
    increment=DB_POOL_INC,
    encoding=DB_ENCODING
)


class DBSessionPool:
    _pool: cx_Oracle.SessionPool
    conn: cx_Oracle.Connection
    instance: DBSessionPool = None

    def __init__(self, pool: cx_Oracle.SessionPool):
        self.pool = pool

    def __enter__(self) -> cx_Oracle.Connection:
        self.conn = self.pool.acquire()
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pool.release(self.conn)

    @classmethod
    def get_instance(cls) -> DBSessionPool:
        if not cls.instance:
            cls.instance = DBSessionPool(_pool)

        return cls.instance
