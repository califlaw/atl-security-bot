from typing import Type

from asyncpg import Record
from telegram import User

from src.dto.base import BaseDTO
from src.dto.exceptions import NotFoundEntity
from src.dto.models import Author


class AuthorDTO(BaseDTO):
    async def try_find_author(
        self, author: User
    ) -> Author | Record | Type[Author]:
        result = await self.db.execute_query(
            """
            select * from author where tg_user_id = %(tg_id)s;
            """,
            params={"tg_id": author.name},
            record=Author,
        )
        if not result:
            raise NotFoundEntity

        return result

    async def set_author(self, author: User) -> Author:
        try:
            if _author := await self.try_find_author(author=author):
                return _author
        except NotFoundEntity:
            return await self.db.execute_query(  # noqa
                """
                insert into author (id, full_name, tg_user_id) 
                values (gen_random_uuid(), %(full_name)s, %(tg_id)s) 
                returning *;
                """,
                params={"tg_id": author.name, "full_name": author.full_name},
                record=Author,
            )
