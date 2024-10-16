from telegram import Update, User
from telegram.ext import ContextTypes

from src.core.transliterate import R
from src.dto.claim import ClaimDTO
from src.dto.models import Claim
from src.handlers.button_cb.enums import CallbackStateEnum
from src.handlers.enums import StatusEnum
from src.handlers.helpers import extract_claim_id
from src.helpers.notify_bot import notify_supergroup


def _decision_msg(user: User) -> str:
    _full_name = " ".join(
        [user.first_name or "", user.last_name or ""]
    ).strip()
    return f"Заявка решена {user.username} ({_full_name})"


async def decision_claim(
    callback_flow: str, update: Update, context: ContextTypes.DEFAULT_TYPE
) -> str | None:
    claim_id = extract_claim_id(context=context)
    claim_obj = ClaimDTO(db=context.bot_data["database"])

    if callback_flow == CallbackStateEnum.resolve.value:
        status = StatusEnum.resolved
    elif callback_flow == CallbackStateEnum.decline.value:
        status = StatusEnum.declined
    else:
        return None

    user: User = update.effective_user
    await claim_obj.resolve_claim(
        claim_id=claim_id,
        decision=_decision_msg(user=user),
        author_id=(await claim_obj.author.try_find_author(author=user)).id,
        status=status,
    )
    await claim_obj.unlock_claim(claim_id=claim_id)

    if status == StatusEnum.resolved:
        claim: Claim = await claim_obj.get_detail_claim(status, claim_id)
        async with notify_supergroup(claim=claim, is_general_group=True):
            await claim_obj.exp_resolved_claims(claim=claim)
            return R.string.found_scammer

    return R.string.thx_decision_claim
