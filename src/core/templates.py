import os
from typing import Dict, LiteralString

import aiofiles
import structlog

from src.core.logger import log_event
from src.core.settings import BASE_DIR
from src.handlers.enums import TemplateFiles

TEMPLATES: Dict = {}
logger: structlog.BoundLogger = structlog.stdlib.get_logger("core.templates")


async def _read_template(path: str | bytes | LiteralString) -> None:
    if ".md" not in path:
        return

    async with aiofiles.open(path, mode="r", encoding="utf-8") as t:
        _, name = os.path.split(path)
        TEMPLATES[name] = await t.read()
        await log_event(logger, message=f"Init file template: {name}")


async def init_templates() -> None:
    for root, _, files in os.walk(os.path.join(BASE_DIR, "src", "templates")):
        for _template in files:
            await _read_template(os.path.join(root, _template))


def render_template(name: str, mapping: dict) -> str:
    if name not in TemplateFiles._value2member_map_:  # noqa
        raise FileNotFoundError(f"Template {name} not found")

    _t: str = TEMPLATES.get(name + ".md")
    return _t.format_map(mapping)
