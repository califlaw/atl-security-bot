from telegram.ext import ContextTypes

from src.handlers.exceptions import ExtractClaimIDError


def extract_claim_id(context: ContextTypes.DEFAULT_TYPE) -> int:
    claim_id = None
    if _claim_id := context.user_data.get("claim", None):
        # safe set variable of claim id
        claim_id = _claim_id

    if not claim_id:
        raise ExtractClaimIDError

    return claim_id
