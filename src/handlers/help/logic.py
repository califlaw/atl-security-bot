import structlog
from telegram import InlineKeyboardButton, Update

from src.core.templates import render_template
from src.handlers.enums import TemplateFiles
from src.handlers.mode import DEFAULT_PARSE_MODE
from src.keyboards.menu import make_reply_markup

logger = structlog.stdlib.get_logger("HelpHandler.logic")


async def help_callback(update: Update, _) -> None:
    button_list = [
        InlineKeyboardButton("Подать жалобу", callback_data="1"),
        InlineKeyboardButton("Что-то еще", callback_data="2"),
    ]
    await logger.ainfo(f"Call info command by {update.message.from_user.name}")

    await update.effective_chat.send_message(
        text=render_template(TemplateFiles.help),
        parse_mode=DEFAULT_PARSE_MODE,
        reply_markup=make_reply_markup(button_list=button_list, colls=1),
    )
