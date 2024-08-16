import io
import os
from typing import Any, List, Tuple

import aiofiles
from asyncpg import Record
from telegram import Document, File, InputFile, PhotoSize
from telegram._utils.files import parse_file_input

from src.core.settings import BASE_DIR, settings
from src.dto.base import BaseDTO
from src.dto.models import Image


class ImageDTO(BaseDTO):
    _claim_id: int

    def get_attachment_path(self, from_root: bool = False):
        _root = BASE_DIR if from_root else ""
        return os.path.join(_root, "attachments", f"claim-{self._claim_id}")

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
                        b_img, tg_type=PhotoSize, filename=file_name
                    )
                )

        return _img_files

    async def save_images(
        self, claim_id: int, images: Tuple[PhotoSize, ...] | Document
    ):
        self._claim_id = claim_id
        img_claim_folder = self.get_attachment_path()
        os.makedirs(img_claim_folder, exist_ok=True)

        if isinstance(images, Document):
            images = [images]  # strong case to list items

        for image in images:
            if (
                isinstance(image, PhotoSize)
                and image.height
                <= settings.getint("DEFAULT", "minHeightImage")
            ):
                break

            img_path = os.path.join(
                img_claim_folder,
                getattr(image, "file_name", image.file_unique_id + ".jpg"),
            )
            await self.db.execute_query(
                """
                insert into image (id, claim_id, image_path) 
                values (gen_random_uuid(), %(claim_id)s, %(image_path)s) 
                returning *;
                """,
                params={"claim_id": claim_id, "image_path": img_path},
                record=Image,
            )
            async with aiofiles.open(img_path, mode="wb") as img:
                buf = io.BytesIO()
                _file: File = await image.get_file()
                await _file.download_to_memory(out=buf)
                await img.write(buf.getbuffer())
