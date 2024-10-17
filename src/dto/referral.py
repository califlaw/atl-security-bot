import hashlib
from datetime import datetime

from telegram import User

from src.dto.author import AuthorDTO
from src.dto.base import BaseDTO
from src.dto.models import Referrer


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

    async def add_referral(self, author: User, referral_code: str) -> None:
        await self.author.create_author(author=author)

        await self.db.execute_query(
            """
            update referrals 
            set referrers = array_append(referrers, %(referral)s)
            where referrer_code = %(referrer_code)s
            """,
            params={
                "referrer_code": referral_code,
                "referral": author.id,
            },
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
