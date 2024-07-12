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

for _phone_hdl in [ComplainHandler]:
    _store_phone_handlers[_phone_hdl.state] = _phone_hdl

for _link_hdl in [CheckLinkHandler]:
    _store_phone_handlers[_link_hdl.state] = _link_hdl


def registration_handlers(application: Application) -> None:
    conversation_url_handler = ConversationHandler(
        entry_points=[
            CommandHandler(StartHandler.command, StartHandler.logic)
        ],
        states={
            state: [
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
            CommandHandler(StartHandler.command, StartHandler.logic)
        ],
        states={
            state: [
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

    check_claim_handler = CommandHandler(
        StartCheckHandler.command, StartCheckHandler.logic
    )
    stat_total_handler = CommandHandler(
        TotalHandler.command, TotalHandler.logic
    )
    help_handler = CommandHandler(HelpHandler.command, HelpHandler.logic)

    application.add_handlers(
        [
            conversation_phone_handler,
            conversation_url_handler,
            check_claim_handler,
            stat_total_handler,
            help_handler,
        ]
    )
