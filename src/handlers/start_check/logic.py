from telegram import InlineKeyboardButton, Update, User
from telegram.ext import ContextTypes

from src.core.templates import render_template
from src.core.transliterate import R
from src.dto.claim import ClaimDTO
from src.dto.models import Claim
from src.handlers.enums import TemplateFiles, StatusEnum
from src.handlers.helpers import extract_claim_id
from src.handlers.mode import DEFAULT_PARSE_MODE
from src.keyboards.menu import make_reply_markup


def _decision_msg(user: User) -> str:
    _full_name = ' '.join([user.first_name or '', user.last_name or '']).strip()
    return (
        f"Заявка решена {user.username} ({_full_name})"
    )


async def start_manage_check_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    button_list = [
        InlineKeyboardButton(R.string.resolve_claim, callback_data="resolved"),
        InlineKeyboardButton(R.string.decline_claim, callback_data="declined"),
    ]

    claim: Claim = await ClaimDTO(
        db=context.bot_data["database"]
    ).get_accepted_claim()
    context.user_data["claim"] = claim.id

    await update.effective_chat.send_message(
        text=render_template(TemplateFiles.start_check, mapping=claim),
        parse_mode=DEFAULT_PARSE_MODE,
        reply_markup=make_reply_markup(button_list=button_list),
    )
    # await update.effective_chat.send_message(text=R.string.comment_decision)


async def decision_claim_button_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    query = update.callback_query
    await query.answer()

    claim_id = extract_claim_id(context=context)
    claim_obj = ClaimDTO(db=context.bot_data["database"])

    flow = query.data
    if flow == "resolved":
        status = StatusEnum.resolved
    elif flow == "declined":
        status = StatusEnum.declined
    else:
        return None

    await claim_obj.resolve_claim(
        claim_id=claim_id,
        decision=_decision_msg(update.effective_user),
        status=status
    )
    await update.effective_chat.send_message(text=R.string.thx_decision_claim)
