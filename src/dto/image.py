import io
import os
from typing import List, Sequence, Tuple

import aiofiles
from telegram import Document, File, InputMediaPhoto, PhotoSize

from src.core.settings import BASE_DIR
from src.dto.base import BaseDTO
from src.dto.models import Image


class ImageDTO(BaseDTO):
    _claim_id: int

    def get_attachment_path(self, from_root: bool = False):
        _root = BASE_DIR if from_root else ""
        return os.path.join(_root, "attachments", f"claim-{self._claim_id}")

    async def attach_images(self, claim_id: int) -> Sequence[InputMediaPhoto]:
        _img_files: Sequence = []
        self._claim_id = claim_id
        images: List[Image] | Image = (
            await self.db.execute_query(  # noqa
                """
                select id, claim_id, image_path 
                from image where claim_id = %(claim_id)s
                """,
                params={"claim_id": claim_id},
                record=Image,
            )
            or []
        )
        if isinstance(images, Image):
            images = [images]  # cast object Image to List[Image]

        for image in images:  # type: Image
            _, file_name = os.path.split(image.image_path)
            async with aiofiles.open(image.image_path, mode="rb") as img:
                b_img: bytes = await img.read()
                _img_files.append(  # noqa
                    InputMediaPhoto(
                        b_img, filename=file_name, has_spoiler=True
                    )
                )

        return _img_files

    async def save_images(
        self, claim_id: int, images: Tuple[PhotoSize, ...] | Document
    ) -> None:
        if not images:
            # on case if empty sequence will on images, and skip create folders
            return

        self._claim_id = claim_id
        img_claim_folder = self.get_attachment_path()
        os.makedirs(img_claim_folder, exist_ok=True)

        for image in images:
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
