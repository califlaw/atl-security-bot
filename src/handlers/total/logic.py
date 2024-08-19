import structlog
from telegram import Update
from telegram.ext import ContextTypes

from src.core.logger import log_event
from src.core.templates import render_template
from src.dto.claim import ClaimDTO
from src.handlers.enums import TemplateFiles

logger = structlog.stdlib.get_logger("TotalHandler.logic")


async def total_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    claim_statistics = await ClaimDTO(
        db=context.bot_data["database"]
    ).statistic_claims()

    _platform_text = ""
    for platform in claim_statistics["platforms"]:
        _name = platform["_name"]
        _counter = platform["_counter"]
        _platform_text += f"- {_name}: {_counter}\n"

    claim_statistics["list_platforms"] = _platform_text

    await log_event(logger, message="Calculate common total information")

    await update.effective_chat.send_message(
        text=render_template(TemplateFiles.total, mapping=claim_statistics),
    )
