from typing import Dict, LiteralString
from uuid import UUID

from asyncpg import Record
from telegram import User

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
        self._image = ImageDTO(db=self.db)
        self._author = AuthorDTO(db=self.db)

    async def initiation_claim(
        self,
        author: User,
        payload: Dict,
    ) -> Claim:
        _key_phone = "phone"
        _strong_field: str = (
            _key_phone if _key_phone in payload.keys() else "link"
        )
        if _strong_field != _key_phone:
            payload[_key_phone] = None
        else:
            payload["link"] = None

        is_missed_fields, _missed_fields = await self.check_missed_payload(
            required_fields=["type", _strong_field],
            payload=payload,
        )
        if is_missed_fields:
            raise MissedFieldsDTOError(f"Missed DTO fields: {_missed_fields}")

        payload["author"]: UUID = (
            await self._author.create_author(author=author)
        ).id

        # phone field normalization value
        if (phone := payload.get(_key_phone)) and _strong_field == _key_phone:
            payload[_key_phone] = normalizer.normalize(phone=phone, as_db=True)

        return await self.db.execute_query(  # noqa
            """
            insert into claims (
                type, author, decision, phone, link, status, platform
            )
            values (
                %(type)s::incidentenum, %(author)s, null, 
                %(phone)s, %(link)s, 'accepted'::statusenum, null
            ) returning *;
            """,
            params=payload,
            record=Claim,
        )

    async def exp_resolved_claims(self, claim_id: int) -> None:
        try:
            claim: Claim = await self.get_detail_claim(
                status=StatusEnum.resolved, claim_id=claim_id
            )
            result_claims: Record = await self.db.execute_query(
                """
                select count(1) as _count 
                from claims cl
                where cl.author = %(author_id)s and status = 'resolved';
                """,
                params={"author_id": claim.author},
            )
            await self._author.inc_exp(
                author_id=claim.author,
                claims_cnt=result_claims.get("_count", 0),
            )
        except NotFoundEntity:
            return

    async def get_detail_claim(
        self,
        status: StatusEnum = StatusEnum.accepted,
        claim_id: int | None = None,
    ) -> Claim:
        params: Dict = {"status": status.value}
        if claim_id:
            sql: LiteralString = """
                select * from claims where status = %(status)s and id = %(id)s
                order by created_at limit 1;
            """
            params["id"] = claim_id
        else:
            sql: LiteralString = """
                select * from claims where status = %(status)s
                order by created_at limit 1;
            """

        claim: Claim | None = await self.db.execute_query(  # noqa
            sql,
            params=params,
            record=Claim,
        )
        if not claim:
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

    async def get_accepted_claim(self) -> Claim | None:
        try:
            claim: Claim = await self.get_detail_claim()
            claim.images = await self._image.attach_images(claim_id=claim.id)
            return claim
        except NotFoundEntity:
            return None

    async def resolve_claim(
        self, claim_id: int, decision: str, status: StatusEnum
    ):
        self._id = claim_id
        await self.db.execute_query(
            """
            update claims set 
                decision = %(decision)s 
            where id = %(id)s;
            """,
            params={"id": claim_id, "decision": decision},
        )
        await self.set_status_claim(status=status)

    async def check_existed_claim(self, phone: str):
        return await self.db.execute_query(
            """
            with
            unique_claim_fraud_cases as (
                select EXISTS (
                    select 1
                    from claims
                    where 
                        phone = %(phone)s and 
                        type = 'phone' and 
                        status = 'resolved'::statusenum
                ) AS exists
            ),
            latest_claim_date AS (
                select MAX(created_at) AS created_at
                from claims
                where 
                    phone = %(phone)s and 
                    type = 'phone' and 
                    status = 'resolved'::statusenum
            ),
            claim_platform AS (
                select platform
                from claims
                where 
                    phone = %(phone)s
                    and type = 'phone'
                    and status = 'resolved'::statusenum
                group by platform
                order by count(1) DESC
                limit 1
            ),
            total_claims AS (
                select count(1) AS total
                from claims
                where 
                    phone = %(phone)s and 
                    type = 'phone' and 
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
            """,
            params={"phone": phone},
        )

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

    async def save_virustotal_analyze(self, claim_id: int, task_result: str):
        await self.db.execute_query(
            """
            insert into malware (type, claim_id) values (%(type)s, %(claim_id)s)
            """,
            params={"claim_id": claim_id, "type": task_result},
        )
