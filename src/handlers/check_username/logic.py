from telegram import Update
from telegram.ext import ContextTypes

from src.core.templates import render_template
from src.core.transliterate import R, effective_message
from src.core.utils import ChatActionContext
from src.dto.claim import ClaimDTO
from src.handlers.check_username.enums import HandleCheckUsernameEnum
from src.handlers.enums import TemplateFiles


async def start_check_username_callback(update: Update, _) -> int:
    await update.effective_chat.send_message(R.string.enter_username)
    return HandleCheckUsernameEnum.AWAIT_USERNAME.value


async def check_username_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    async with ChatActionContext(
        context.bot, chat_id=update.effective_chat.id
    ):
        existed_claim = await ClaimDTO(
            db=context.bot_data["database"]
        ).check_existed_claim(username=update.message.text)

    if not existed_claim:
        await effective_message(update, message=R.string.username_not_found)
    else:
        await effective_message(
            update,
            message=render_template(
                TemplateFiles.check_phone_claim, mapping=existed_claim
            ),
        )

    await effective_message(update, message=R.string.thx_security_kg_alga)
    return HandleCheckUsernameEnum.STOP_CONVERSATION.value
