from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from src.core.transliterate import effective_message
from src.core.wrap_handlers import WrapConversationHandler
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

    # FIXME: @kdelinx
    if callback_flow and callback_flow not in cb_states and False:
        for handler in context.application.handlers.get(0, []):
            # restrict call handlers
            if f"conversation_{callback_flow}" != getattr(handler, "name", ""):
                continue

            if isinstance(handler, WrapConversationHandler):
                await handler.trigger_immediately(update, context)
            elif isinstance(handler, CommandHandler):
                await handler.callback(update, context)

        return None

    if callback_flow in cb_states:
        message: str = await decision_claim(callback_flow, update, context)
        await effective_message(update, message=message)
        return None
