import structlog
from telegram import InlineKeyboardButton, Update
from telegram.ext import ContextTypes

from src.core.settings import settings
from src.core.templates import render_template
from src.core.transliterate import R
from src.core.utils import ChatActionContext
from src.handlers.enums import TemplateFiles
from src.keyboards.menu import make_reply_markup

logger = structlog.stdlib.get_logger("HelpHandler.logic")


async def help_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    button_list = [
        InlineKeyboardButton(
            R.string.ask_help_group,
            url=settings.get("bot", "communityGroupLink"),
        ),
    ]
    await logger.ainfo(f"Call info command by {update.message.from_user.name}")

    async with ChatActionContext(
        context.bot, chat_id=update.effective_chat.id
    ):
        await update.effective_chat.send_message(
            text=render_template(TemplateFiles.help),
            reply_markup=make_reply_markup(button_list=button_list),
        )
