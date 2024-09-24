import structlog
from telegram import InlineKeyboardButton, Update

from src.core.settings import settings
from src.core.templates import render_template
from src.core.transliterate import R, effective_message
from src.handlers.enums import TemplateFiles
from src.keyboards.menu import make_reply_markup

logger = structlog.stdlib.get_logger("StartHandler.logic")


async def start_callback(update: Update, _) -> None:
    button_list = [
        InlineKeyboardButton(
            R.string.join_community,
            url=settings.get("bot", "communityGroupLink"),
        ),
    ]

    await effective_message(
        update,
        message=render_template(
            TemplateFiles.start,
            mapping={"help_group": settings.get("bot", "helpGroupName")},
        ),
        reply_markup=make_reply_markup(button_list=button_list),
    )
