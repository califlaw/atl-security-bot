from typing import Dict, LiteralString
from uuid import UUID

from asyncpg import Record
from telegram import User

from src.core.enums import ExperienceEnum
from src.core.normalizer import NormalizePhoneNumber
from src.dto.author import AuthorDTO
from src.dto.base import BaseDTO
from src.dto.exceptions import MissedFieldsDTOError, NotFoundEntity
from src.dto.image import ImageDTO
from src.dto.models import Claim
from src.handlers.enums import StatusEnum

normalizer = NormalizePhoneNumber()


class ClaimDTO(BaseDTO):
    _id: int

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # init nested DTO models
        self.image = ImageDTO(db=self.db)
        self.author = AuthorDTO(db=self.db)

    async def initiation_claim(
        self,
        author: User,
        payload: Dict,
    ) -> Claim:
        _key_phone = "phone"
        keys = ["phone", "username", "link"]
        strong_field = next(
            (key for key in keys if key in payload), _key_phone
        )

        # normalize fields of checking not nullable and case eq `strong_field`
        payload["phone"] = (
            payload["phone"] if strong_field == "phone" else None
        )
        payload["username"] = (
            payload["username"] if strong_field == "username" else None
        )
        payload["link"] = payload["link"] if strong_field == "link" else None

        is_missed_fields, _missed_fields = await self.check_missed_payload(
            required_fields=["type", strong_field],
            payload=payload,
        )
        if is_missed_fields:
            raise MissedFieldsDTOError(f"Missed DTO fields: {_missed_fields}")

        payload["author"]: UUID = (
            await self.author.create_author(author=author)
        ).id

        # phone field normalization value
        if (phone := payload.get(_key_phone)) and strong_field == _key_phone:
            payload[_key_phone] = normalizer.normalize(phone=phone, as_db=True)

        return await self.db.execute_query(  # noqa
            """
            insert into claims (
                type, author, decision, phone, link, username, status, platform
            )
            values (
                %(type)s::incidentenum, %(author)s, null, 
                %(phone)s, %(link)s, %(username)s, 'accepted'::statusenum, null
            ) returning *;
            """,
            params=payload,
            record=Claim,
        )

    async def exp_resolved_claims(self, claim: Claim | int) -> None:
        try:
            if isinstance(claim, int):
                claim: Claim = await self.get_detail_claim(
                    status=StatusEnum.resolved, claim_id=claim
                )

            await self.author.inc_exp(
                author_id=claim.author,
                exp=ExperienceEnum.processing_claim,
            )
        except NotFoundEntity:
            return

    async def get_detail_claim(
        self,
        status: StatusEnum = StatusEnum.accepted,
        claim_id: int | None = None,
        tg_user_id: int | None = None,
        skip_raise_error: bool = False,
    ) -> Claim:
        params: Dict = {"status": status.value}
        if claim_id:
            sql: LiteralString = """
                select * from claims 
                where status = %(status)s and id = %(id)s and is_locked = false
                order by created_at limit 1;
            """
            params["id"] = claim_id
        elif tg_user_id:
            sql: LiteralString = """
                select cl.* from claims cl
                join author au on au.id = cl.author
                where (
                    is_locked = true and
                    cl.status = %(status)s and 
                    au.tg_user_id = %(tg_user_id)s 
                )
                order by cl.created_at limit 1;
            """
            params["tg_user_id"] = tg_user_id
        else:
            sql: LiteralString = """
                select * from claims 
                where status = %(status)s and is_locked = false
                order by created_at limit 1;
            """

        claim: Claim | None = await self.db.execute_query(  # noqa
            sql,
            params=params,
            record=Claim,
        )
        if not claim and skip_raise_error is False:
            raise NotFoundEntity

        return claim

    async def set_status_claim(self, status: StatusEnum):
        assert self._id is not None, "Attribute _id is required, missed value!"

        if status not in StatusEnum._value2member_map_:  # noqa
            raise KeyError(f"{status} not included key in StatusEnum")

        await self.db.execute_query(
            """
            update claims set status = %(status)s where id = %(id)s;
            """,
            params={"id": self._id, "status": status.value},
        )

    async def set_platform_claim(self, platform: str):
        await self.db.execute_query(
            """
            update claims set platform = %(platform)s where id = %(id)s;
            """,
            params={"id": self._id, "platform": platform},
        )

    async def get_accepted_claim(self, tg_user_id: int) -> Claim | None:
        claim: Claim | None = None

        try:
            claim: Claim = await self.get_detail_claim(
                status=StatusEnum.accepted, tg_user_id=tg_user_id
            )
        except NotFoundEntity:
            # try find new accepted claim, if not found locked by user
            claim: Claim = await self.get_detail_claim(
                status=StatusEnum.accepted, skip_raise_error=True
            )
        finally:
            if claim:
                claim.images = await self.image.attach_images(
                    claim_id=claim.id
                )
                await self.lock_claim(claim_id=claim.id, tg_user_id=tg_user_id)

        return claim

    async def resolve_claim(
        self, claim_id: int, decision: str, author_id: UUID, status: StatusEnum
    ):
        self._id = claim_id
        await self.db.execute_query(
            """
            update claims set 
                decision = %(decision)s, processed_by = %(processed_by)s
            where id = %(id)s;
            """,
            params={
                "id": claim_id,
                "decision": decision,
                "processed_by": author_id,
            },
        )
        await self.set_status_claim(status=status)

    async def check_existed_claim(
        self,
        link: str | None = None,
        phone: str | None = None,
        username: str | None = None,
    ) -> Record:
        """
        Checks the existence of claims based on the provided phone number,
         username, or link.

        Depending on the passed parameters (`phone`, `username`, or `link`),
         the function:
          - Executes a query to the database to check for a claim with the
          corresponding type (phone, username, or link).
          - Returns data about the claim's existence, the date of the latest
          claim, the platform, and the total number of claims.

        Args:
            phone (str, optional): The phone number to check for claims.
            username (str, optional): The username to check for claims.
            link (str, optional): The link to check for claims.

        Returns:
            Type: [Record] - Contains the following keys:
                - `_existed_claim` (bool): Indicates whether a claim exists.
                - `_last_claim` (datetime): The date of the last claim.
                - `_platform_claim` (str): The platform with the highest number
                of claims.
                - `_total_claims` (int): The total number of claims.

        Raises:
            ValueError: If none of `phone`, `username`, or `link` is provided.
        """
        params = {}
        conditions = []

        if phone:
            conditions.append("phone = %(phone)s")
            params["phone"] = phone
            claim_type = "phone"
        elif username:
            conditions.append("username = %(username)s")
            params["username"] = username
            claim_type = "username"
        elif link:
            conditions.append("link = %(link)s")
            params["link"] = link
            claim_type = "link"
        else:
            raise ValueError(
                "At least one of 'phone', 'username', "
                "or 'link' must be provided"
            )

        # Join conditions using AND
        where_clause = " and ".join(conditions)

        query = f"""
        with
        unique_claim_fraud_cases as (
            select EXISTS (
                select 1
                from claims
                where 
                    {where_clause} and 
                    type = '{claim_type}' and 
                    status = 'resolved'::statusenum
            ) AS exists
        ),
        latest_claim_date AS (
            select MAX(created_at) AS created_at
            from claims
            where 
                {where_clause} and 
                type = '{claim_type}' and 
                status = 'resolved'::statusenum
        ),
        claim_platform AS (
            select platform
            from claims
            where 
                {where_clause}
                and type = '{claim_type}'
                and status = 'resolved'::statusenum
            group by platform
            order by count(1) DESC
            limit 1
        ),
        total_claims AS (
            select count(1) AS total
            from claims
            where 
                {where_clause} and 
                type = '{claim_type}' and 
                status = 'resolved'::statusenum
        )
        select ucf.exists     AS _existed_claim,
               lid.created_at AS _last_claim,
               fp.platform    AS _platform_claim,
               tc.total       AS _total_claims
        from unique_claim_fraud_cases ucf
                 cross join latest_claim_date lid
                 cross join claim_platform fp
                 cross join total_claims tc;
        """

        return await self.db.execute_query(query, params=params)  # noqa

    async def statistic_claims(self):
        result = {}
        totals = await self.db.execute_query(
            """
            select distinct 
                count(id) as total_claim, 
                count(id) filter (where status = 'resolved') as resolved_claims 
            from claims;
            """
        )
        # there are queries could return Nonetype, if not found platforms
        _platforms_records = (
            await self.db.execute_query(
                """
                select c2.platform
                from claims c1
                join claims c2 on c1.id <> c2.id
                where similarity(c1.platform, c2.platform) >= 0.8
                group by 
                    c2.platform, c1.platform, 
                    similarity(c1.platform, c2.platform);
                """
            )
            or []
        )
        if isinstance(_platforms_records, Record):
            # type cast record to list objects, on the way fetch one row
            _platforms_records = [_platforms_records]
        platforms = await self.db.execute_query(
            " union all ".join(  # noqa
                f"""
                    select '{record['platform']}' as _name, count(*) as _counter
                    from claims
                    where 
                        similarity(platform, '{record['platform']}') > 0.7 and 
                        status = 'resolved'::statusenum
                    """
                for record in _platforms_records
            )
        )
        if isinstance(platforms, Record):
            # type cast record to list objects, on the way fetch one row
            platforms = [platforms]

        result.update(totals)
        result["platforms"] = platforms or []
        return result

    async def check_existed_linked_claim(self, link: str):
        return await self.db.execute_query(
            """
            select 
                cm.id as id, cm.platform as platform, 
                cm.link as link, m.type as type
            from claims cm
                     join malware m on cm.id = m.claim_id
            where cm.link = %(link)s and cm.status = 'resolved'::statusenum;
            """,
            params={"link": link},
            record=Claim,
        )

    async def check_existed_username_claim(self, username: str):
        return await self.db.execute_query(
            """
            select 
                platform, username, type
            from claims
            where username = %(username)s and status = 'resolved'::statusenum;
            """,
            params={"username": username},
            record=Claim,
        )

    async def save_virustotal_analyze(self, claim_id: int, task_result: str):
        await self.db.execute_query(
            """
            insert into malware (type, claim_id) values (%(type)s, %(claim_id)s)
            """,
            params={"claim_id": claim_id, "type": task_result},
        )

    async def lock_claim(self, claim_id: int, tg_user_id: int) -> None:
        await self.db.execute_query(
            """
            update claims 
            set 
                is_locked = true, lock_id = %(tg_user_id)s 
            where id = %(id)s and status = 'accepted'::statusenum;
            """,
            params={"id": claim_id, "tg_user_id": tg_user_id},
        )

    async def unlock_claim(self, claim_id: int) -> None:
        await self.db.execute_query(
            """
            update claims 
            set 
                is_locked = false, lock_id = null 
            where (
                id = %(id)s and 
                is_locked = true and 
                status in ('resolved', 'declined')
            );
            """,
            params={"id": claim_id},
        )
