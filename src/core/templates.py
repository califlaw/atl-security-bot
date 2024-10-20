import os
import re
from typing import Dict, LiteralString, Type

import aiofiles
import structlog
from telegram.helpers import escape_markdown

from src.core.logger import log_event
from src.core.normalizer import type_normalizer
from src.core.settings import BASE_DIR
from src.core.transliterate import R
from src.core.utils import v2_allowed_symbol_regex
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
    name: str,
    mapping: Type[BaseRecord] | dict | None = None,
    entity_type: str | None = None,
) -> str:
    if name not in TemplateFiles._value2member_map_:  # noqa
        raise FileNotFoundError(f"Template {name} not found")

    _t: str = TEMPLATES.get(name + ".md")

    try:
        if not mapping:
            mapping = {}
        mapper_values = type_normalizer(mapping)
        logger.debug("Prepared values for rendering: %s", mapper_values)
        text_template = _t.format_map(mapper_values)
    except KeyError as e:
        logger.exception(f"Error of rendering template {name} with var: %s", e)
        text_template = R.string.error_template

    _version = 1 if re.findall(v2_allowed_symbol_regex, text_template) else 2

    return escape_markdown(
        text_template, version=_version, entity_type=entity_type
    )
