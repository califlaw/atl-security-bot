import collections
import itertools
import re
from typing import Any, Dict, List, Tuple

import asyncpg
from asyncpg import Connection, Pool, Record

from src.core.settings import settings


class DBPool:
    _pool: Pool = None

    async def init_db(self):
        self._pool = await asyncpg.create_pool(
            dsn=settings.get("database", "dsn"),
            max_size=settings.getint("database", "poolSize"),
        )
        return self

    @staticmethod
    def _format2psql(
        query: str, named_args: Dict[str, Any]
    ) -> Tuple[str, List[Any]]:
        positional_generator = itertools.count(1)
        positional_map = collections.defaultdict(
            lambda: "${}".format(next(positional_generator))
        )

        # reformat SQL string to ascii style
        query = re.sub(r"\s+", " ", query).strip().lower()
        for key in named_args.keys():
            query = query.replace(f"%({key})s", positional_map[key])

        positional_items = sorted(
            positional_map.items(),
            key=lambda item: int(item[1].replace("$", "")),
        )
        positional_args = [
            named_args[named_arg] for named_arg, _ in positional_items
        ]
        return query, positional_args

    async def close(self):
        await self._pool.close()

    async def execute_query(
        self, query: str, params: Dict[str, Any] | None = None
    ) -> List[Record] | None:
        _query, positional_args = self._format2psql(
            query=query, named_args=params
        )
        async with self._pool.acquire() as conn:  # type: Connection
            try:
                if "insert" in _query or "update" in _query:
                    await conn.execute(query, positional_args)
                else:
                    return await conn.fetch(query, positional_args)
            finally:
                await self._pool.release(conn)
