import os
from typing import Dict, LiteralString

import aiofiles

from src.core.settings import BASE_DIR

TEMPLATES: Dict = {}


async def _read_template(path: str | bytes | LiteralString) -> None:
    if ".md" not in path:
        return

    async with aiofiles.open(path, mode="r", encoding="utf-8") as t:
        _, name = os.path.split(path)
        TEMPLATES[name] = await t.read()


async def init_templates() -> None:
    for root, _, files in os.walk(os.path.join(BASE_DIR, "src", "templates")):
        for _template in files:
            await _read_template(os.path.join(root, _template))
