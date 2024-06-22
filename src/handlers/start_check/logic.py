from telegram import InlineKeyboardButton, Update
from telegram.ext import ContextTypes

from src.core.templates import render_template
from src.dto.claim import Claim
from src.handlers.mode import DEFAULT_PARSE_MODE
from src.keyboards.menu import make_reply_markup


async def check_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    pass
