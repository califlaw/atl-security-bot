from telegram import Update
from telegram.ext import ContextTypes

from src.core.templates import render_template
from src.core.utils import ChatActionContext
from src.dto.claim import Claim
from src.keyboards.menu import make_reply_markup


async def check_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    pass
