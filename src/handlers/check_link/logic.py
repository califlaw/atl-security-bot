from telegram import Update
from telegram.ext import ContextTypes

from src.core.templates import render_template
from src.core.transliterate import R, effective_message
from src.core.utils import ChatActionContext
from src.core.virustotal import VirusTotal
from src.dto.claim import ClaimDTO
from src.dto.models import Claim
from src.handlers.check_link.enums import HandleCheckLinkEnum
from src.handlers.enums import TemplateFiles
from src.helpers.notify_bot import notify_supergroup


async def start_check_link_callback(update: Update, _) -> int:
    await update.effective_chat.send_message(R.string.enter_link)
    return HandleCheckLinkEnum.AWAIT_LINK.value


async def parse_link_process_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    created_claim: Claim | None = None
    link = update.message.text  # link with optional schema
    claim_obj = ClaimDTO(db=context.bot_data["database"])

    claim: Claim = await claim_obj.check_existed_linked_claim(link=link)
    if not claim:
        created_claim: Claim = await claim_obj.initiation_claim(
            author=update.effective_user,
            payload={"link": link, "type": "link"},
        )
        claim: Claim = await claim_obj.check_existed_linked_claim(link=link)

    async with ChatActionContext(
        context.bot, chat_id=update.effective_chat.id
    ):
        vt = VirusTotal()

        result: dict = {
            "_existed_claim": claim is not None,
            "_malware_type": vt.translate_type(
                getattr(claim, "type", None), default=R.string.claim_not_found
            ),  # malware type
        }

        await effective_message(
            update,
            message=render_template(
                TemplateFiles.check_link_claim, mapping=result
            ),
        )

        if created_claim:
            async with notify_supergroup(
                claim=await claim_obj.get_detail_claim(
                    claim_id=created_claim.id
                )
            ):
                pass

    await effective_message(update, message=R.string.dont_follow_links)

    return HandleCheckLinkEnum.STOP_CONVERSATION.value
