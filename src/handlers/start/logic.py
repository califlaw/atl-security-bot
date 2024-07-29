import structlog
from telegram import InlineKeyboardButton, Update
from telegram.ext import ContextTypes

from src.core.settings import settings
from src.core.templates import render_template
from src.handlers.enums import TemplateFiles
from src.handlers.mode import DEFAULT_PARSE_MODE
from src.keyboards.menu import make_reply_markup

logger = structlog.stdlib.get_logger("StartHandler.logic")


async def start_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    button_list = [
        InlineKeyboardButton(
            "Добавляйтесь в чат-комьюнити",
            url=settings.get("bot", "communityGroupLink"),
        ),
    ]

    await update.effective_chat.send_message(
        text=render_template(TemplateFiles.start),
        parse_mode=DEFAULT_PARSE_MODE,
        reply_markup=make_reply_markup(button_list=button_list),
    )
