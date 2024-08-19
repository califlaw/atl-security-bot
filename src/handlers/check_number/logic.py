from telegram import Update
from telegram.ext import ContextTypes

from src.core.normalizer import NormalizePhoneNumber, type_normalizer
from src.core.templates import render_template
from src.core.transliterate import R
from src.core.utils import ChatActionContext
from src.dto.claim import ClaimDTO
from src.handlers.check_number.enums import HandleCheckPhoneEnum
from src.handlers.enums import TemplateFiles
from src.handlers.mode import DEFAULT_PARSE_MODE

normalizer = NormalizePhoneNumber()


async def start_check_phone_callback(update: Update, _) -> int:
    await update.effective_chat.send_message(R.string.enter_phone)
    return HandleCheckPhoneEnum.AWAIT_PHONE.value


async def check_number_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    async with ChatActionContext(
        context.bot, chat_id=update.effective_chat.id
    ):
        existed_claim = await ClaimDTO(
            db=context.bot_data["database"]
        ).check_existed_claim(
            phone=normalizer.normalize(update.message.text, as_db=True)
        )

    await update.effective_chat.send_message(
        text=render_template(
            TemplateFiles.check_claim, mapping=type_normalizer(existed_claim)
        ),
        parse_mode=DEFAULT_PARSE_MODE,
    )
