import io
import os
from dataclasses import dataclass
from io import BufferedReader
from typing import Dict, List, Sequence

import aiofiles
from asyncpg import Record
from telegram import Document, File

from src.core.settings import BASE_DIR
from src.dto.base import BaseDTO
from src.handlers.enums import StatusEnum


@dataclass(kw_only=True)
class Claim(BaseDTO):
    _id: int

    def get_attachment_path(self, from_root: bool = False):
        _root = BASE_DIR if from_root else ""
        return os.path.join(_root, "attachments", str(self._id))

    async def _attach_images(self) -> List[bytes]:
        _img_files = []
        images = await self.db.execute_query(  # type: Record
            "select id, image_path from image where id = %(id)s",
            params={"id": self._id},
        )
        for image in images:
            _path = self.get_attachment_path(from_root=True)
            async with aiofiles.open(
                f"{_path}/{image.image_path}", mode="rb"
            ) as img:
                _img_files.append(await img.read())

        return _img_files

    async def _save_images(self, images: Sequence[Document]):
        _path = self.get_attachment_path()
        os.makedirs(_path, exist_ok=True)
        for image in images:
            async with aiofiles.open(
                f"{_path}/{image.file_name}", mode="wb"
            ) as img:
                buf = io.BytesIO()
                _file = await image.get_file()  # type: File
                await _file.download_to_memory(out=buf)
                await img.write(buf.getbuffer())

    async def initiation_claim(
        self, payload: Dict, images: Sequence[BufferedReader] | None = None
    ):
        claim = await self.db.execute_query(
            """
            insert into claims values () returning id;
            """,
            params=payload,
        )
        if images:
            claim.id

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
        claim = await self.db.execute_query(
            """
            select * from claims where status = 'accepted' 
            order by created_at limit 1
            """
        )
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
