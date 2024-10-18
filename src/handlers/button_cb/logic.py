from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from src.core.transliterate import effective_message
from src.handlers.button_cb.enums import CallbackStateEnum
from src.handlers.button_cb.flows.claim import decision_claim


async def button_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    query = update.callback_query
    await query.answer()
    callback_flow = query.data

    cb_states = [
        CallbackStateEnum.resolve.value,
        CallbackStateEnum.decline.value,
    ]

    if callback_flow in cb_states:
        message: str = await decision_claim(callback_flow, update, context)
        await effective_message(update, message=message)
        return None
