from typing import Sequence

import structlog
from telegram import InlineKeyboardButton, PhotoSize, Update
from telegram.ext import ContextTypes

from src.core.logger import log_event
from src.core.transliterate import R
from src.core.utils import get_link
from src.dto.claim import ClaimDTO, normalizer
from src.dto.image import ImageDTO
from src.handlers.complain.enums import HandlerStateEnum
from src.handlers.exceptions import ExtractClaimIDError
from src.handlers.helpers import extract_claim_id
from src.keyboards.menu import make_reply_markup

logger = structlog.stdlib.get_logger("handlers.complain")


async def complain_phone_callback(update: Update, _) -> int:
    await update.effective_chat.send_message(R.string.enter_phone_number)
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
    if phone:
        payload["type"] = "phone"
        payload["phone"] = phone
    else:
        payload["type"] = "link"
        payload["link"] = get_link(url=source_claim)

    claim = await ClaimDTO(db=context.bot_data["database"]).initiation_claim(
        author=update.effective_user,
        payload=payload,
        images=None,
    )

    context.user_data["claim"] = claim.id
    await update.message.reply_text(R.string.ask_claim_platform)

    return HandlerStateEnum.AWAIT_PLATFORM.value


async def complain_parse_platform_ask_photos_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    platform = update.message.text
    try:
        claim_id: int = extract_claim_id(context)
    except ExtractClaimIDError:
        return HandlerStateEnum.STOP_CONVERSATION.value

    await log_event(
        logger,
        f"Acquire platform: {platform} for claim",
        payload={"claim_id": claim_id},
    )

    dto = ClaimDTO(db=context.bot_data["database"])
    dto._id = claim_id  # set `claim_id` attribute param
    await dto.set_platform_claim(platform=platform)

    button_list = [
        InlineKeyboardButton(
            R.string.skip_add_images,
            callback_data="skip_photos",
        ),
    ]

    await update.message.reply_text(
        text=R.string.attach_images,
        reply_markup=make_reply_markup(button_list=button_list, colls=1),
    )

    return HandlerStateEnum.AWAIT_PHOTOS.value


async def complain_parse_photos_or_stop_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    images: Sequence[PhotoSize] = update.message.photo

    try:
        claim_id = extract_claim_id(context=context)
    except ExtractClaimIDError:
        return HandlerStateEnum.STOP_CONVERSATION.value
    finally:
        if not images:
            return HandlerStateEnum.STOP_CONVERSATION.value

    dto = ImageDTO(db=context.bot_data["database"])
    await dto.save_images(claim_id=claim_id, images=images)

    await update.message.reply_text(R.string.thx_finish_claim)
    return HandlerStateEnum.STOP_CONVERSATION.value


async def fallback_exit_conv_callback(update: Update, _) -> int:
    query = update.callback_query
    is_answer = await query.answer()
    if not is_answer or query.data == "skip_photos":
        return HandlerStateEnum.STOP_CONVERSATION.value

    await update.message.reply_text(R.string.thx_finish_claim)
    return HandlerStateEnum.STOP_CONVERSATION.value
