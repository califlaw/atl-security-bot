from telegram import Update
from telegram.ext import ContextTypes

from src.core.enums import CommandEnum
from src.core.transliterate import effective_message
from src.handlers.button_cb.enums import CallbackStateEnum
from src.handlers.button_cb.flows.claim import decision_claim


async def button_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    from src.handlers import (
        CheckNumberHandler,
        CheckUsernameHandler,
        StartCheckLinkHandler,
        StartComplainHandler,
        StartHandler,
    )

    query = update.callback_query
    await query.answer()
    callback_flow = query.data

    if callback_flow in [
        CallbackStateEnum.resolve.value,
        CallbackStateEnum.decline.value,
    ]:
        message: str = await decision_claim(callback_flow, update, context)
        await effective_message(update, message=message)
        return None

    match callback_flow:
        case CommandEnum.START.value:
            await StartHandler.logic(update, context)
        case CommandEnum.COMPLAIN.value:
            await StartComplainHandler.logic(update, context)
        case CommandEnum.CHECK_LINK.value:
            await StartCheckLinkHandler.logic(update, context)
        case CommandEnum.CHECK_USERNAME.value:
            await CheckUsernameHandler.logic(update, context)
        case CommandEnum.CHECK_NUMBER.value:
            await CheckNumberHandler.logic(update, context)

        case _:
            return None
