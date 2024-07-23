import structlog
from telegram import Update
from telegram.ext import ContextTypes

from src.core.logger import log_event
from src.core.templates import render_template
from src.dto.claim import Claim
from src.handlers.enums import TemplateFiles
from src.handlers.mode import DEFAULT_PARSE_MODE

logger = structlog.stdlib.get_logger("TotalHandler.logic")


async def total_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    stat_mapping = await Claim(
        db=context.bot_data["database"]
    ).statistic_claims()

    _platform_text = ""
    for platform in stat_mapping["platforms"]:
        _name = platform["name"]
        _counter = platform["counter"]
        _platform_text += f"- {_name}: {_counter}\n"

    stat_mapping["list_platforms"] = _platform_text

    await log_event(logger, message="Calculate common total information")

    await update.effective_chat.send_message(
        text=render_template(TemplateFiles.total, mapping=stat_mapping),
        parse_mode=DEFAULT_PARSE_MODE,
    )
