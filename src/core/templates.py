import os
from typing import Dict, LiteralString, Type

import aiofiles
import structlog
from telegram.helpers import escape_markdown

from src.core.logger import log_event
from src.core.normalizer import type_normalizer
from src.core.settings import BASE_DIR
from src.core.transliterate import R
from src.dto.models import BaseRecord
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


def render_template(
    name: str, mapping: Type[BaseRecord] | dict | None = None
) -> str:
    if name not in TemplateFiles._value2member_map_:  # noqa
        raise FileNotFoundError(f"Template {name} not found")

    _t: str = TEMPLATES.get(name + ".md")

    try:
        if not mapping:
            mapping = {}
        text_template = _t.format_map(type_normalizer(mapping))
    except KeyError:
        text_template = R.string.error_template

    return escape_markdown(text_template, version=2, entity_type=None)
