from telegram import InlineKeyboardButton, Update
from telegram.ext import ContextTypes

from src.core.settings import settings
from src.core.templates import render_template
from src.core.transliterate import R
from src.dto.claim import ClaimDTO
from src.dto.models import Claim
from src.handlers.enums import TemplateFiles
from src.handlers.mode import DEFAULT_PARSE_MODE
from src.keyboards.menu import make_reply_markup


async def start_manage_check_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if update.effective_user.name not in settings.getlist(
        "bot", "operators", fallback=[]
    ):
        return

    button_list = [
        InlineKeyboardButton(R.string.resolve_claim, callback_data="resolved"),
        InlineKeyboardButton(R.string.decline_claim, callback_data="declined"),
    ]

    claim: Claim = await ClaimDTO(
        db=context.bot_data["database"]
    ).get_accepted_claim()

    await update.effective_chat.send_message(
        text=render_template(TemplateFiles.start_check, mapping=claim),
        parse_mode=DEFAULT_PARSE_MODE,
        reply_markup=make_reply_markup(button_list=button_list, colls=1),
    )
