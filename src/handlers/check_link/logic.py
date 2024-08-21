from telegram import Update
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown

from src.core.templates import render_template
from src.core.transliterate import R
from src.core.utils import ChatActionContext
from src.dto.claim import ClaimDTO
from src.dto.models import Claim
from src.handlers.check_link.enums import HandleCheckLinkEnum
from src.handlers.enums import TemplateFiles


async def start_check_link_callback(update: Update, _) -> int:
    await update.effective_chat.send_message(R.string.enter_link)
    return HandleCheckLinkEnum.AWAIT_LINK.value


async def parse_link_process_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    async with ChatActionContext(
        context.bot, chat_id=update.effective_chat.id
    ):
        claim: Claim = await ClaimDTO(
            db=context.bot_data["database"]
        ).check_existed_linked_claim(link=update.message.text)
        result: dict = {
            "_existed_claim": claim is not None,
            "_type_claim": getattr(claim, "type", R.string.unknown_type),
        }

    await update.effective_chat.send_message(
        text=render_template(TemplateFiles.check_link_claim, mapping=result),
    )
    await update.effective_chat.send_message(
        text=escape_markdown(
            R.string.dont_follow_links, version=2, entity_type=None
        )
    )

    return HandleCheckLinkEnum.STOP_CONVERSATION.value
