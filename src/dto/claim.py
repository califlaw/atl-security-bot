from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Literal, Self, Sequence

from telegram import Document, User

from src.core.normalizer import NormalizePhoneNumber
from src.dto.author import Author
from src.dto.base import BaseDTO
from src.dto.image import Image
from src.handlers.enums import StatusEnum

normalizer = NormalizePhoneNumber()


@dataclass(kw_only=True)
class Claim(BaseDTO):
    _id: int
    _author: Author

    id: int | None
    status: StatusEnum | None
    created_at: datetime | None
    type: Literal["phone", "url"] | None
    comment: str | None
    decision: str | None
    phone: str | None
    link: str | None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # init nested DTO models
        self._image = Image(db=self.db)
        self._author = Author(db=self.db)

    async def initiation_claim(
        self,
        author: User,
        payload: Dict,
        images: Sequence[Document] | None = None,
    ):
        _key_phone = "phone"
        _strong_field: str = (
            _key_phone if _key_phone in payload.keys() else "link"
        )
        await self.check_payload(
            required_fields=["type", _strong_field],
            payload=payload,
        )
        payload["author"] = self._from_record(
            await self._author.set_author(author=author)
        ).id

        # phone field normalization value
        if phone := payload.get(_key_phone) and _strong_field == _key_phone:
            payload[_key_phone] = normalizer.normalize(phone=phone, as_db=True)

        claim: Claim = self._from_record(
            await self.db.execute_query(
                """
                insert into claims (type, author, decision, phone, link, status)
                values (
                    '%(type)s', '%(author)s', null, 
                    '%(phone)s', '%(link)s', 'accepted'
                ) returning id;
                """,
                params=payload,
                record=self.__class__,
            )
        )
        if images:
            await self._image.save_images(claim_id=claim.id, images=images)

    async def get_detail_claim(
        self, status: StatusEnum = StatusEnum.accepted
    ) -> Self:
        claim = await self.db.execute_query(
            f"""
            select * from claims where status = '{status.value}' 
            order by created_at limit 1
            """,
            record=self.__class__,
        )
        return self._from_record(claim)

    async def set_status_claim(self, status: StatusEnum):
        if status not in StatusEnum._value2member_map_:  # noqa
            raise KeyError(f"{status} not included key in StatusEnum")

        await self.db.execute_query(
            """
            update claims set status = %(status)s where id = %(id)
            """,
            params={"id": self._id, "status": status.value},
        )

    async def get_accepted_claim(self):
        claim = await self.get_detail_claim()
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
