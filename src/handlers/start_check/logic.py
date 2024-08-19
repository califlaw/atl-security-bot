from telegram import InlineKeyboardButton, Update
from telegram.ext import ContextTypes

from src.core.templates import render_template
from src.core.transliterate import R
from src.dto.claim import ClaimDTO
from src.dto.models import Claim
from src.handlers.button_cb.enums import CallbackStateEnum
from src.handlers.enums import TemplateFiles
from src.keyboards.menu import make_reply_markup


async def start_manage_check_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    button_list = [
        InlineKeyboardButton(
            R.string.resolve_claim,
            callback_data=CallbackStateEnum.resolve.value,
        ),
        InlineKeyboardButton(
            R.string.decline_claim,
            callback_data=CallbackStateEnum.decline.value,
        ),
    ]

    claim: Claim = await ClaimDTO(
        db=context.bot_data["database"]
    ).get_accepted_claim()
    context.user_data["claim"] = claim.id

    await update.effective_chat.send_message(
        text=render_template(TemplateFiles.start_check, mapping=claim),
        reply_markup=make_reply_markup(button_list=button_list),
    )
