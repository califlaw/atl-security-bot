from typing import Final

import structlog
from telegram import InlineKeyboardButton, Update
from telegram.ext import ContextTypes

from src.core.settings import settings
from src.core.templates import render_template
from src.core.transliterate import R, effective_message
from src.core.utils import ChatActionContext
from src.dto.author import AuthorDTO
from src.handlers.enums import TemplateFiles
from src.handlers.start.enums import HandlerStateEnum
from src.keyboards.menu import make_reply_markup

logger = structlog.stdlib.get_logger("StartHandler.logic")

SKIP_REGISTER_USER: Final[str] = "skip_register_user"


async def start_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    button_list = [
        InlineKeyboardButton(
            R.string.join_community,
            url=settings.get("bot", "communityGroupLink"),
        ),
    ]

    async with ChatActionContext(
        context.bot, chat_id=update.effective_chat.id
    ):
        await effective_message(
            update,
            message=render_template(TemplateFiles.start),
            reply_markup=make_reply_markup(button_list=button_list),
        )

    # remove on next release for continue flow of conversation user
    return HandlerStateEnum.STOP_CONVERSATION.value


async def ask_user_phone_callback(update: Update, _) -> int:
    button_list = [
        InlineKeyboardButton(
            R.string.join_community,
            callback_data=SKIP_REGISTER_USER,
        ),
    ]

    await effective_message(
        update,
        message=R.string.enter_phone,
        reply_markup=make_reply_markup(button_list=button_list),
    )
    return HandlerStateEnum.AWAIT_EMAIL.value


async def parse_user_phone_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    phone_number = update.message.text
    author_obj = AuthorDTO(db=context.bot_data["database"])

    await author_obj.set_phone(phone=phone_number)
    await effective_message(update, message=R.string.thx_will_on_call)
    await effective_message(update, message=R.string.enter_email)

    return HandlerStateEnum.AWAIT_EMAIL.value


async def query_start_button_cb_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int | None:
    query = update.callback_query
    await query.answer()
    callback_handler_data: str = query.data

    if callback_handler_data == SKIP_REGISTER_USER:
        return HandlerStateEnum.STOP_CONVERSATION.value
