import structlog
from telegram import Update
from telegram.ext import ContextTypes

from src.core.logger import log_event
from src.dto.claim import ClaimDTO
from src.handlers.complain.enums import HandlerStateEnum

logger = structlog.stdlib.get_logger("handlers.complain")


async def complain_phone_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    await update.effective_chat.send_message("Введите номер телефона")
    return HandlerStateEnum.AWAIT_PHONE.value


async def complain_parse_phone_ask_platform_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    await log_event(
        logger, "Fetch message", payload={"msg": update.message.text}
    )
    await ClaimDTO(db=context.bot_data["database"]).initiation_claim(
        author=update.effective_user,
        payload={"phone": update.message.text, "type": "phone"},
        images=None,
    )
    await update.message.reply_text(
        "Место инцидента? (lalafo.kg, instagram, и тд)"
    )

    return HandlerStateEnum.AWAIT_PLATFORM.value
