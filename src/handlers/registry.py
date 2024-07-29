from collections import defaultdict
from typing import Type

from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from . import *

_store_link_handlers = defaultdict()
_store_phone_handlers = defaultdict()

for _phone_hdl in [
    ParsePhoneOrLinkWithAskPlatformHandler,
    ParsePlatformAskPhotosHandler,
    ParsePhotosOrStopConvHandler,
]:
    _store_phone_handlers[_phone_hdl.state] = _phone_hdl

for _link_hdl in []:
    _store_link_handlers[_link_hdl.state] = _link_hdl


def registration_handlers(application: Application) -> None:
    conversation_url_handler = ConversationHandler(
        entry_points=[
            CommandHandler(
                StartCheckLinkHandler.command, StartCheckLinkHandler.logic
            )
        ],
        states={
            state.value: [
                CallbackQueryHandler(callback=klass.logic)
                if klass.is_query and not klass.filters
                else MessageHandler(
                    filters=klass.filters, callback=klass.logic
                )
            ]  # type: klass: Type[BaseHandlerKlass]
            for (state, klass) in _store_link_handlers.items()
        },
        fallbacks=[MessageHandler(filters.Regex("^Done$"), lambda: None)],
        name="conversation_link",
        persistent=False,
    )

    conversation_phone_handler = ConversationHandler(
        entry_points=[
            CommandHandler(
                StartComplainHandler.command, StartComplainHandler.logic
            )
        ],
        states={
            state.value: [
                CallbackQueryHandler(callback=klass.logic)
                if klass.is_query and not klass.filters
                else MessageHandler(
                    filters=klass.filters, callback=klass.logic
                )
            ]  # type: klass: Type[BaseHandlerKlass]
            for (state, klass) in _store_phone_handlers.items()
        },
        fallbacks=[MessageHandler(filters.Regex("^Done$"), lambda: None)],
        name="conversation_phone",
        persistent=False,
    )

    help_handler = CommandHandler(HelpHandler.command, HelpHandler.logic)
    start_handler = CommandHandler(StartHandler.command, StartHandler.logic)

    # manager commands
    start_check_claim_handler = CommandHandler(
        StartCheckHandler.command, StartCheckHandler.logic
    )
    stat_total_handler = CommandHandler(
        TotalHandler.command, TotalHandler.logic
    )

    application.add_handlers(
        [
            conversation_phone_handler,
            conversation_url_handler,
            start_check_claim_handler,
            stat_total_handler,
            start_handler,
            help_handler,
        ]
    )
