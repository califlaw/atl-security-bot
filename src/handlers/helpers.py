from typing import Type

from telegram.ext import ContextTypes

from src.handlers.exceptions import ExtractClaimIDError


def extract_claim_id(
    context: ContextTypes.DEFAULT_TYPE,
) -> int | Type[Exception]:
    claim_id: int | None = None
    if _claim_id := context.user_data.get("claim", None):
        # safe set variable of claim id
        claim_id = _claim_id

    if not claim_id:
        raise ExtractClaimIDError

    return claim_id
