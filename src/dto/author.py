from asyncpg import Record
from telegram import User

from src.dto.base import BaseDTO
from src.dto.exceptions import NotFoundEntity


class Author(BaseDTO):
    async def try_find_author(self, author: User) -> Record["Author"]:
        result = await self.db.execute_query(
            """
            select * from author where tg_user_id = '%(tg_id)s'
            """,
            params={"tg_id": author.id},
        )
        if not result:
            raise NotFoundEntity

        return result

    async def set_author(self, author: User) -> Record[int]:
        try:
            if _author := await self.try_find_author(author=author):
                return _author.id
        except NotFoundEntity:
            return await self.db.execute_query(
                """
                insert into author (id, full_name, tg_user_id) 
                values (gen_random_uuid(), '%(full_name)', '%(tg_id)s') 
                returning id;
                """,
                params={"tg_id": author.id, "full_name": author.name},
            )
