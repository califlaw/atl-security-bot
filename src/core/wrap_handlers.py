import asyncio

from telegram import Update
from telegram.ext import (
    ApplicationHandlerStop,
    ContextTypes,
    ConversationHandler,
)


class WrapConversationHandler(ConversationHandler):
    async def trigger_immediately(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        This is run whenever a conversation has timed out.
        Also makes sure that all handlers which are in the :attr:`TIMEOUT`
        state and whose :meth:`BaseHandler.check_update` returns
        :obj:`True` is handled.
        """
        # Now run all handlers which are START state
        for handler in self.entry_points:
            self._update_state(
                asyncio.create_task(handler.callback), self._get_key(update)
            )

            try:
                await handler.handle_update(
                    update, context.application, True, context
                )
            except ApplicationHandlerStop:
                continue

        print(self._conversations)
