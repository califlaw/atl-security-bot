from typing import Dict
from uuid import UUID

from telegram import User

from src.core.normalizer import NormalizePhoneNumber
from src.dto.author import AuthorDTO
from src.dto.base import BaseDTO
from src.dto.exceptions import MissedFieldsDTOError
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
            await self._author.set_author(author=author)
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

    async def get_detail_claim(
        self, status: StatusEnum = StatusEnum.accepted
    ) -> Claim:
        return await self.db.execute_query(  # noqa
            """
            select * from claims where status = %(status)s 
            order by created_at limit 1
            """,
            params={"status": status.value},
            record=Claim,
        )

    async def set_status_claim(self, status: StatusEnum):
        assert self._id is not None, "Attribute _id is required, missed value!"

        if status not in StatusEnum._value2member_map_:  # noqa
            raise KeyError(f"{status} not included key in StatusEnum")

        await self.db.execute_query(
            """
            update claims set status = %(status)s where id = %(id)s
            """,
            params={"id": self._id, "status": status.value},
        )

    async def set_platform_claim(self, platform: str):
        await self.db.execute_query(
            """
            update claims set platform = %(platform)s where id = %(id)s
            """,
            params={"id": self._id, "platform": platform},
        )

    async def get_accepted_claim(self):
        claim: Claim = await self.get_detail_claim()
        claim.images = await self._image.attach_images(claim_id=claim.id)

        return claim

    async def resolve_claim(
        self, claim_id: int, decision: str, status: StatusEnum
    ):
        self._id = claim_id
        await self.db.execute_query(
            """
            update claims set 
                decision = %(decision)s 
            where id = %(id)s
            """,
            params={"id": claim_id, "decision": decision},
        )
        await self.set_status_claim(status=status)

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
        _platforms_records = await self.db.execute_query(
            """
            SELECT c2.platform
            FROM claims c1
            JOIN claims c2 ON c1.id <> c2.id
            WHERE similarity(c1.platform, c2.platform) >= 0.8
            GROUP BY 
                c2.platform, c1.platform, similarity(c1.platform, c2.platform);
            """
        )
        platforms = await self.db.execute_query(
            " UNION ALL ".join(  # noqa
                f"""
                    SELECT '{record['platform']}' as _name, count(*) as _counter
                    FROM claims
                    WHERE 
                        similarity(platform, '{record['platform']}') > 0.7 and 
                        status = 'resolved'
                    """
                for record in _platforms_records
            )
        )

        result.update(totals)
        result["platforms"] = platforms
        return result
