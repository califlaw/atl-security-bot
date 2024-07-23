import io
import os
from typing import Any, List, Sequence

import aiofiles
from asyncpg import Record
from telegram import Document, File, InputFile
from telegram._utils.files import parse_file_input

from src.core.database import DBPool
from src.core.settings import BASE_DIR
from src.dto.base import BaseDTO
from src.dto.models import Image


class ImageDTO(BaseDTO):
    def __init__(self, db: DBPool, *args, **kwargs):
        super().__init__(db, *args, **kwargs)

    def get_attachment_path(self, from_root: bool = False):
        _root = BASE_DIR if from_root else ""
        return os.path.join(_root, "attachments", f"claim-{self.claim_id}")

    async def attach_images(
        self, claim_id: int
    ) -> List[str | InputFile | Any]:
        _img_files = []
        images: List[Record] = await self.db.execute_query(
            "select id, image_path from image where claim_id = %(claim_id)s",
            params={"claim_id": claim_id},
            record=Image,
        )
        for image in images:  # type: Image
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

    async def save_images(self, claim_id: int, images: Sequence[Document]):
        self.claim_id = claim_id
        _path = self.get_attachment_path()
        os.makedirs(_path, exist_ok=True)
        for image in images:
            _path = os.path.join(_path, image.file_name)
            async with aiofiles.open(_path, mode="wb") as img:
                buf = io.BytesIO()
                _file: File = await image.get_file()
                await _file.download_to_memory(out=buf)
                await img.write(buf.getbuffer())
