import os
from typing import Dict

import aiofiles

from src.core.settings import BASE_DIR

TEMPALTES: Dict = {}


async def _read_template(path: str) -> None:
    if '.md' not in path:
        return

    async with aiofiles.open(path, mode='r', encoding='utf-8') as t:
        _, name = os.path.split(path)
        TEMPALTES[name] = await t.read()


async def init_templates() -> None:
    for (root, _, files) in os.walk(os.path.join(BASE_DIR, 'src', 'templates')):
        for _template in files:
            await _read_template(os.path.join(root, _template).decode())
