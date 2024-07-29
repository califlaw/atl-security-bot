import structlog
from telegram import Update
from telegram.ext import ContextTypes

from src.core.logger import log_event
from src.core.utils import get_link
from src.dto.claim import ClaimDTO, normalizer
from src.handlers.complain.enums import HandlerStateEnum

logger = structlog.stdlib.get_logger("handlers.complain")


async def complain_phone_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    await update.effective_chat.send_message("Введите номер телефона")
    return HandlerStateEnum.AWAIT_PHONE_OR_LINK.value


async def complain_parse_phone_or_link_ask_platform_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    payload = {}
    source_claim: str = update.message.text
    await log_event(
        logger, "Fetch source claim", payload={"msg": source_claim}
    )

    phone: str | None = normalizer.try_is_phone(phone=source_claim)
    if not phone:
        payload["type"] = "link"
        payload["link"] = get_link(url=source_claim)
    else:
        payload["type"] = "phone"
        payload["phone"] = phone

    claim = await ClaimDTO(db=context.bot_data["database"]).initiation_claim(
        author=update.effective_user,
        payload=payload,
        images=None,
    )
    context.user_data["claim"] = claim.id
    await update.message.reply_text(
        "Место инцидента? (lalafo.kg, instagram, и тд)"
    )

    return HandlerStateEnum.AWAIT_PLATFORM.value


async def complain_parse_platform_ask_photos_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    claim_id = None
    platform = update.message.text
    if _claim_id := context.user_data.get("claim", None):
        # safe set variable of claim id
        claim_id = _claim_id

    if not claim_id:
        await log_event(logger, "Missed claim identifier! Stop conversation.")
        return HandlerStateEnum.STOP_CONVERSATION.value

    await log_event(
        logger,
        f"Acquire platform: {platform} for claim",
        payload={"claim_id": claim_id},
    )

    dto = ClaimDTO(db=context.bot_data["database"])
    dto._id = claim_id
    await dto.set_platform_claim(platform=platform)

    await update.message.reply_text("Прикрепите фотографии инцидента")

    return HandlerStateEnum.AWAIT_PHOTOS.value
