from typing import List, Any

import asyncpg
from asyncpg import Connection, Pool, Record

from src.core.settings import settings


class DBPool:
    _pool: Pool = None

    @classmethod
    async def init_db(cls):
        cls._pool = await asyncpg.create_pool(
            dsn=settings.get("database", "dsn"),
            max_size=settings.get("database", "poolSize"),
        )

    async def close(self):
        await self._pool.close()

    async def execute_query(
        self, query: str, params: List[str | int | Any]
    ) -> List[Record] | None:
        async with self._pool.acquire() as conn:  # type: Connection
            try:
                if "insert" in query.lower():
                    await conn.execute(query, params)
                else:
                    return await conn.fetch(query, params)
            finally:
                await self._pool.release(conn)
