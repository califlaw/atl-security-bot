import structlog
from telegram import InlineKeyboardButton, Update

from src.core.settings import settings
from src.core.templates import render_template
from src.core.transliterate import R
from src.handlers.enums import TemplateFiles
from src.handlers.mode import DEFAULT_PARSE_MODE
from src.keyboards.menu import make_reply_markup

logger = structlog.stdlib.get_logger("StartHandler.logic")


async def start_callback(update: Update, _) -> None:
    button_list = [
        InlineKeyboardButton(
            R.string.join_community,
            url=settings.get("bot", "communityGroupLink"),
        ),
    ]
    R.string.set_language(update.effective_user.language_code)

    await update.effective_chat.send_message(
        text=render_template(TemplateFiles.start),
        parse_mode=DEFAULT_PARSE_MODE,
        reply_markup=make_reply_markup(button_list=button_list),
    )
