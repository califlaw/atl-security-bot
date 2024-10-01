from typing import Tuple

import structlog
from telegram import Bot, Document, PhotoSize, Update
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown

from src.core.logger import log_event
from src.core.transliterate import R, effective_message
from src.core.utils import create_bg_task, get_link
from src.core.virustotal import VirusTotal
from src.dto.claim import ClaimDTO, normalizer
from src.dto.image import ImageDTO
from src.dto.models import Claim
from src.handlers.complain.enums import HandlerStateEnum
from src.handlers.exceptions import ExtractClaimIDError
from src.handlers.helpers import extract_claim_id
from src.helpers.notify_bot import notify_supergroup

logger = structlog.stdlib.get_logger("handlers.complain")


async def complain_phone_callback(update: Update, _) -> int:
    await effective_message(update, message=R.string.enter_phone_or_link)
    return HandlerStateEnum.AWAIT_PHONE_OR_LINK.value


async def complain_parse_phone_or_link_ask_platform_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    payload = {}
    source_claim: str = update.message.text
    await log_event(
        logger, "Fetch source claim", payload={"msg": source_claim}
    )
    claim_obj = ClaimDTO(db=context.bot_data["database"])

    phone: str | None = normalizer.try_is_phone(phone=source_claim)
    if phone:
        payload["type"] = "phone"
        payload["phone"] = phone
    else:
        payload["type"] = "link"
        payload["link"] = get_link(url=source_claim)

    if not payload.get("phone") and not payload.get("link"):
        await effective_message(
            update, message=R.string.incorrect_phone, is_reply=True
        )
        return HandlerStateEnum.AWAIT_PHONE_OR_LINK.value

    claim: Claim = await claim_obj.initiation_claim(
        author=update.effective_user,
        payload=payload,
    )

    context.user_data["claim"] = claim.id
    if url := payload.get("link"):  # type: str
        vt = VirusTotal()
        await create_bg_task(
            vt.scan_url(url=url, wait_for_completion=True),
            claim_obj.save_virustotal_analyze,
            ctx={"claim_id": claim.id},
        )

    await effective_message(
        update, message=R.string.ask_claim_platform, is_reply=True
    )
    async with notify_supergroup(claim=claim):  # type: Bot
        pass

    return HandlerStateEnum.AWAIT_PLATFORM.value


async def complain_parse_platform_ask_photos_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    platform = update.message.text
    try:
        claim_id: int = extract_claim_id(context)
    except ExtractClaimIDError:
        await effective_message(update, message=R.string.lost_claim_id)
        return HandlerStateEnum.STOP_CONVERSATION.value

    await log_event(
        logger,
        f"Acquire platform: {platform} for claim",
        payload={"claim_id": claim_id},
    )

    claim_obj = ClaimDTO(db=context.bot_data["database"])
    claim_obj._id = claim_id  # set `claim_id` attribute param
    await claim_obj.set_platform_claim(platform=platform)

    await effective_message(
        update,
        message=R.string.attach_images,
        is_reply=True,
    )

    return HandlerStateEnum.AWAIT_PHOTOS.value


async def complain_parse_photos_or_stop_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    images: Tuple[PhotoSize, ...] = update.message.photo
    if not images:
        images: Document = update.message.document

    try:
        claim_id = extract_claim_id(context=context)
    except ExtractClaimIDError:
        await effective_message(update, message=R.string.lost_claim_id)
        return HandlerStateEnum.STOP_CONVERSATION.value
    finally:
        if not images:
            return HandlerStateEnum.STOP_CONVERSATION.value

    image_obj = ImageDTO(db=context.bot_data["database"])
    await image_obj.save_images(claim_id=claim_id, images=images)

    await effective_message(
        update, message=R.string.thx_finish_claim, is_reply=True
    )
    return HandlerStateEnum.STOP_CONVERSATION.value


async def fallback_exit_conv_callback(update: Update, _) -> int:
    query = update.callback_query
    await query.answer()

    text = escape_markdown(
        R.string.thx_finish_claim, version=2, entity_type=None
    )
    await query.message.chat.send_message(text=text)
    return HandlerStateEnum.STOP_CONVERSATION.value
