from telegram import Update
from telegram.ext import ContextTypes

from src.handlers.button_cb.enums import CallbackStateEnum
from src.handlers.button_cb.flows.claim import decision_claim


async def button_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    query = update.callback_query
    await query.answer()
    callback_flow = query.data

    if callback_flow in [
        CallbackStateEnum.resolve.value,
        CallbackStateEnum.decline.value,
    ]:
        message: str = await decision_claim(callback_flow, update, context)
        await update.effective_chat.send_message(text=message)
