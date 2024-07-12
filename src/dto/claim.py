import io
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Literal, Sequence

import aiofiles
from asyncpg import Record
from telegram import Document, File, InputFile, User
from telegram._utils.files import parse_file_input

from src.core.normalizer import NormalizePhoneNumber
from src.core.settings import BASE_DIR
from src.dto.author import Author
from src.dto.base import BaseDTO
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
        self._author = Author(db=self.db)

    def get_attachment_path(self, from_root: bool = False):
        _root = BASE_DIR if from_root else ""
        return os.path.join(_root, "attachments", f"claim-{self._id}")

    async def _attach_images(self) -> List[str | InputFile | Any]:
        _img_files = []
        images: List[Record] = await self.db.execute_query(
            "select id, image_path from image where id = %(id)s",
            params={"id": self._id},
        )
        for image in images:
            _, file_name = os.path.split(image.image_path)
            _path = self.get_attachment_path(from_root=True)
            async with aiofiles.open(
                f"{_path}/{image.image_path}", mode="rb"
            ) as img:
                b_img: bytes = await img.read()
                _img_files.append(
                    parse_file_input(
                        b_img, tg_type=Document, filename=file_name
                    )
                )

        return _img_files

    async def _save_images(self, images: Sequence[Document]):
        _path = self.get_attachment_path()
        os.makedirs(_path, exist_ok=True)
        for image in images:
            _path = os.path.join(_path, image.file_name)
            async with aiofiles.open(_path, mode="wb") as img:
                buf = io.BytesIO()
                _file: File = await image.get_file()
                await _file.download_to_memory(out=buf)
                await img.write(buf.getbuffer())

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
        payload["author"] = (await self._author.set_author(author=author)).id

        # phone field normalization value
        if phone := payload.get(_key_phone) and _strong_field == _key_phone:
            payload[_key_phone] = normalizer.normalize(phone=phone, as_db=True)

        claim: Record = await self.db.execute_query(
            """
            insert into claims (type, author, decision, phone, link, status)
            values (
                '%(type)s', '%(author)s', null, 
                '%(phone)s', '%(link)s', 'accepted'
            ) returning id;
            """,
            params=payload,
        )
        if images:
            self._id = claim.id
            await self._save_images(images=images)

    async def get_detail_claim(self, status: StatusEnum = StatusEnum.accepted):
        claim = await self.db.execute_query(
            f"""
            select * from claims where status = '{status.value}' 
            order by created_at limit 1
            """
        )
        return self.__class__(**claim, db=None)

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
        self._id = claim.id
        claim.images = await self._attach_images()

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
