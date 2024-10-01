from uuid import UUID

from asyncpg import Record
from telegram import User

from src.core.enums import AuthorRankEnum, ExperienceEnum
from src.dto.base import BaseDTO
from src.dto.exceptions import NotFoundEntity
from src.dto.models import Author
from src.helpers.manage_user import promote_user


class AuthorDTO(BaseDTO):
    async def get_by_id(self, _id: UUID) -> Author | Record:
        result = await self.db.execute_query(
            """
            select * from author where id = %(id)s;
            """,
            params={"id": _id},
            record=Author,
        )
        if not result:
            raise NotFoundEntity

        return result

    async def try_find_author(self, author: User) -> Author | Record:
        result = await self.db.execute_query(
            """
            select * from author where tg_user_id = %(tg_user_id)s;
            """,
            params={"tg_user_id": author.id},
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
                insert into author (full_name, tg_username, tg_user_id) 
                values (
                    %(full_name)s, %(tg_username)s, %(tg_id)s
                ) 
                returning *;
                """,
                params={
                    "tg_user_id": author.id,
                    "tg_username": author.name,
                    "full_name": author.full_name,
                },
                record=Author,
            )

    async def inc_exp(self, author_id: UUID, claims_cnt: int = 0):
        author: Author = await self.get_by_id(_id=author_id)

        match claims_cnt:
            case cnt if 0 < cnt <= 5:
                exp = ExperienceEnum.simple
            case cnt if 5 < cnt <= 10:
                exp = ExperienceEnum.modern
            case cnt if 10 < cnt <= 50:
                exp = ExperienceEnum.advanced
            case _:
                exp = ExperienceEnum.simple

        await self.db.execute_query(
            """
            update author 
            set 
                exp = exp + %(inc)s::int 
            where id = %(author_id)s; 
            """,
            params={"inc": exp.value, "author_id": author_id},
        )

        if author:
            await promote_user(
                author_id=author_id,
                author_obj=self,
                custom_title=AuthorRankEnum.pro.value,  # noqa
            )
