import hashlib
from datetime import datetime
from typing import List, LiteralString

from telegram import User

from src.core.enums import ExperienceEnum
from src.dto.author import AuthorDTO
from src.dto.base import BaseDTO
from src.dto.models import Author, Referrer


class ReferralDTO(BaseDTO):
    _id: int

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # init nested DTO models
        self.author = AuthorDTO(db=self.db)

    async def initiation_referral(self, author: User) -> Referrer:
        payload = {
            "author_id": (await self.author.create_author(author=author)).id,
        }

        hash_code: float = author.id + datetime.now().timestamp()  # gen hash

        payload["referrer_code"] = str(
            hashlib.md5(str(hash_code).encode()).hexdigest()[:6]
        )
        return await self.db.execute_query(  # noqa
            """
            insert into referrals (
                author_id, referrer_code
            )
            values (
                %(author_id)s, %(referrer_code)s
            )
            on conflict (author_id) 
            do update set author_id = referrals.author_id
            returning *;
            """,
            params=payload,
            record=Referrer,
        )

    async def get_referral(
        self, author: User | None = None, referral_code: str | None = None
    ) -> Referrer:
        params = {}
        conditions = []
        query: LiteralString = "select * from referrals"

        if referral_code:
            conditions.append("referrer_code = %(referral_code)s")
            params["referral_code"] = referral_code

        if author:
            conditions.append("author_id = %(author_id)s")
            params["author_id"] = author.id

        if conditions:
            query += " where " + " and ".join(conditions)

        return await self.db.execute_query(  # noqa
            query=query,
            params=params,
            record=Referrer,
        )

    async def add_referral(self, author: User, referral_code: str) -> None:
        user: Author = await self.author.create_author(author=author)
        referral: Referrer = await self.get_referral(
            referral_code=referral_code
        )

        if referral and referral.author_id == user.id:
            return

        referral_count: int = await self.db.execute_query(  # noqa
            """
            with _rows as (
                update referrals 
                set referrers = array_append(referrers, %(referral)s)
                where (
                    not (%(referral)s = any(referrers)) and
                    referrer_code = %(referrer_code)s 
                ) 
                returning 1
            )
            select count(1) as _count from _rows;
            """,
            params={
                "referrer_code": referral_code,
                "referral": author.id,
            },
        )
        if referral_count:
            await self.author.inc_exp(
                author_id=referral.author_id, exp=ExperienceEnum.invite_people
            )

    async def get_referral_positions(self, author: User) -> int:
        author_id = (await self.author.try_find_author(author=author)).id

        referral_count = await self.db.execute_query(
            """
            select array_length(referrers, 1) as _count
            from referrals 
            where author_id = %(author_id)s
            """,
            params={"author_id": author_id},
        )
        return referral_count.get("_count", 0)

    async def get_ranked_users(self) -> List:
        return await self.db.execute_query(
            """
            select 
                r.author_id, 
                au.tg_username as username,
                array_length(referrers, 1) as _count 
            from referrals as r 
            join author as au on r.author_id = au.id
            group by r.author_id, r.referrers, username 
            order by _count desc
            limit 5
            """
        )
