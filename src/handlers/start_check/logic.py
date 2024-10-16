from telegram import InlineKeyboardButton, Update
from telegram.ext import ContextTypes

from src.core.templates import render_template
from src.core.transliterate import R, effective_message
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

    claim: Claim | None = await ClaimDTO(
        db=context.bot_data["database"]
    ).get_accepted_claim(tg_user_id=update.effective_user.id)

    if not claim:
        await effective_message(update, message=R.string.claim_not_found)
        return

    context.user_data["claim"] = claim.id  # set context of `claim` type: int

    if not claim.link:
        claim.link = ""  # allow empty line in template then None

    if claim.images:
        await update.effective_chat.send_media_group(claim.images)
    await effective_message(
        update,
        message=render_template(TemplateFiles.start_check, mapping=claim),
        reply_markup=make_reply_markup(button_list=button_list),
    )
