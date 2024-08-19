from collections import defaultdict
from typing import Type

from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
)

from . import *

_store_claim_handlers = defaultdict()

_check_link_handlers = defaultdict()
_check_phone_handlers = defaultdict()

for _phone_hdl in [
    ParsePhoneOrLinkWithAskPlatformHandler,
    ParsePlatformAskPhotosHandler,
    ParsePhotosOrStopConvHandler,
]:
    _store_claim_handlers[_phone_hdl.state] = _phone_hdl

for _phone_check_hdl in [ParseCheckPhoneHandler]:
    _check_phone_handlers[_phone_check_hdl.state] = _phone_check_hdl

for _link_check_hdl in []:
    _check_link_handlers[_link_check_hdl.state] = _link_check_hdl


def registration_handlers(application: Application) -> None:
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
            for (state, klass) in _store_claim_handlers.items()
        },
        fallbacks=[
            CallbackQueryHandler(callback=ExitFallbackPhoneConvHandler.logic)
        ],
        name="conversation_phone",
        persistent=False,
    )

    conversation_phone_check_handler = ConversationHandler(
        entry_points=[
            CommandHandler(
                CheckNumberHandler.command, CheckNumberHandler.logic
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
            for (state, klass) in _check_phone_handlers.items()
        },
        fallbacks=[
            CallbackQueryHandler(callback=ExitFallbackPhoneConvHandler.logic)
        ],
        name="conversation_check_phone",
        persistent=False,
    )

    help_handler = CommandHandler(HelpHandler.command, HelpHandler.logic)
    start_handler = CommandHandler(StartHandler.command, StartHandler.logic)

    # manager commands
    start_check_claim_handler = CommandHandler(
        StartCheckHandler.command, StartCheckHandler.logic
    )
    buttons_cb_handler = CallbackQueryHandler(ButtonCallbacksHandler.logic)
    stat_total_handler = CommandHandler(
        TotalHandler.command, TotalHandler.logic
    )

    application.add_handlers(
        [
            conversation_phone_check_handler,
            conversation_phone_handler,
            start_check_claim_handler,
            buttons_cb_handler,
            stat_total_handler,
            start_handler,
            help_handler,
        ]
    )
