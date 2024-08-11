from dataclasses import dataclass
from typing import Dict, Sequence
from uuid import UUID

from telegram import Document, User

from src.core.normalizer import NormalizePhoneNumber
from src.dto.author import AuthorDTO
from src.dto.base import BaseDTO
from src.dto.exceptions import MissedFieldsDTOError
from src.dto.image import ImageDTO
from src.dto.models import Claim
from src.handlers.enums import StatusEnum

normalizer = NormalizePhoneNumber()


@dataclass
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
        images: Sequence[Document] | None = None,
    ) -> Claim:
        _key_phone = "phone"
        payload["link"] = None
        payload["phone"] = None
        _strong_field: str = (
            _key_phone if _key_phone in payload.keys() else "link"
        )

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

        claim: Claim = await self.db.execute_query(  # noqa
            """
            insert into claims (
                type, author, decision, phone, link, status, platform
            )
            values (
                %(type)s::incidentenum, %(author)s, null, 
                %(phone)s, %(link)s, 'accepted'::statusenum, null
            ) returning id;
            """,
            params=payload,
            record=Claim,
        )
        if images:
            await self._image.save_images(claim_id=claim.id, images=images)

        return claim

    async def get_detail_claim(
        self, status: StatusEnum = StatusEnum.accepted
    ) -> Claim:
        return await self.db.execute_query(  # noqa
            """
            select * from claims where status = %(status)s 
            order by created_at limit 1
            """,
            params={'status': status.value},
            record=Claim,
        )

    async def set_status_claim(self, status: StatusEnum):
        if status not in StatusEnum._value2member_map_:  # noqa
            raise KeyError(f"{status} not included key in StatusEnum")

        await self.db.execute_query(
            """
            update claims set status = %(status)s where id = %(id)
            """,
            params={"id": self._id, "status": status.value},
        )

    async def set_platform_claim(self, platform: str):
        await self.db.execute_query(
            """
            update claims set platform = %(platform)s where id = %(id)
            """,
            params={"id": self._id, "platform": platform},
        )

    async def get_accepted_claim(self):
        claim: Claim = await self.get_detail_claim()
        claim.images = await self._image.attach_images(claim_id=claim.id)

        return claim

    async def resolve_claim(
        self, claim_id: int, decision: str, comment: str | None = None
    ):
        self._id = claim_id
        await self.db.execute_query(
            """
            update claims set comment = %(comment)s, 
            decision = %(decision)s where id = %(id)s
            """,
            params={"id": claim_id, "decision": decision, "comment": comment},
        )
        await self.set_status_claim(status=StatusEnum.resolved)

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
        platforms = await self.db.execute_query(
            """
            select distinct 
                count(id) as total_claim, 
                count(id) filter (where status = 'resolved') as resolved_claims 
            from claims;
            """
        )

        result.update(totals)
        result["platforms"] = platforms
        return result
