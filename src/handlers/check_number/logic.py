from telegram import Update
from telegram.ext import ContextTypes

from src.core.templates import render_template
from src.core.transliterate import R
from src.core.utils import ChatActionContext
from src.dto.claim import ClaimDTO, normalizer
from src.handlers.check_number.enums import HandleCheckPhoneEnum
from src.handlers.enums import TemplateFiles


async def start_check_phone_callback(update: Update, _) -> int:
    await update.effective_chat.send_message(R.string.enter_phone)
    return HandleCheckPhoneEnum.AWAIT_PHONE.value


async def check_number_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    async with ChatActionContext(
        context.bot, chat_id=update.effective_chat.id
    ):
        existed_claim = await ClaimDTO(
            db=context.bot_data["database"]
        ).check_existed_claim(
            normalizer.normalize(phone=update.message.text, as_db=True)
        )

    await update.effective_chat.send_message(
        text=render_template(
            TemplateFiles.check_phone_claim, mapping=existed_claim
        ),
    )
    await update.effective_chat.send_message(
        text=R.string.thx_security_kg_alga
    )

    return HandleCheckPhoneEnum.STOP_CONVERSATION.value
