from telegram import CallbackQuery, InlineKeyboardButton, Update
from telegram.ext import ContextTypes

from src.core.templates import render_template
from src.dto.claim import Claim
from src.handlers.enums import HandlerStateEnum
from src.handlers.mode import DEFAULT_PARSE_MODE
from src.keyboards.menu import make_reply_markup


async def complain_phone_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> HandlerStateEnum:
    query: CallbackQuery = update.callback_query
    await query.answer()
    await query.edit_message_text("")

    return HandlerStateEnum.TYPING_REPLY.value
