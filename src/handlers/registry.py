from collections import defaultdict
from enum import Enum
from typing import Dict, List, Type

from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
)

from . import *

_start_conv_handlers = defaultdict()
_store_claim_handlers = defaultdict()

_check_link_handlers = defaultdict()
_check_phone_handlers = defaultdict()
_check_username_handlers = defaultdict()


# register handlers in store dictionary
for _start_hdl in [
    ButtonStartCallbacksHandler,
    AskStartUserPhoneOrSkipHandler,
]:
    _start_conv_handlers[_start_hdl.state] = _start_hdl

for _phone_hdl in [
    ParsePhoneOrLinkWithAskPlatformHandler,
    ParsePlatformAskPhotosHandler,
    ParsePhotosOrStopConvHandler,
]:
    _store_claim_handlers[_phone_hdl.state] = _phone_hdl

for _phone_check_hdl in [ParseCheckPhoneHandler]:
    _check_phone_handlers[_phone_check_hdl.state] = _phone_check_hdl

for _username_check_hdl in [ParseCheckUsernameHandler]:
    _check_username_handlers[_username_check_hdl.state] = _username_check_hdl

for _link_check_hdl in [ParseLinkCheckProcessHandler]:
    _check_link_handlers[_link_check_hdl.state] = _link_check_hdl


def _prepare_states(
    store: Dict[Enum, Type[BaseHandlerKlass]],
) -> Dict[int, List[MessageHandler | CallbackQueryHandler]]:
    return {
        # for correctly register query handler without enum state (will None)
        getattr(state, "value", None): [
            CallbackQueryHandler(callback=klass.logic)
            if klass.is_query and not klass.filters
            else MessageHandler(filters=klass.filters, callback=klass.logic)
        ]  # type: klass: Type[BaseHandlerKlass]
        for (state, klass) in store.items()
    }


def registration_handlers(application: Application) -> None:
    conversation_start_conv_handler = WrapConversationHandler(
        entry_points=[
            CommandHandler(StartHandler.command, StartHandler.logic)
        ],
        states=_prepare_states(store=_start_conv_handlers),
        fallbacks=[],
        name=f"conversation_{CommandEnum.START.value}",
        allow_reentry=False,
        persistent=False,
    )

    conversation_fetch_source_handler = WrapConversationHandler(
        entry_points=[
            CommandHandler(
                StartComplainHandler.command, StartComplainHandler.logic
            )
        ],
        states=_prepare_states(store=_store_claim_handlers),
        fallbacks=[
            CallbackQueryHandler(callback=ExitFallbackPhoneConvHandler.logic)
        ],
        name=f"conversation_{CommandEnum.COMPLAIN.value}",
        allow_reentry=True,
        persistent=False,
    )

    conversation_phone_check_handler = WrapConversationHandler(
        entry_points=[
            CommandHandler(
                CheckNumberHandler.command, CheckNumberHandler.logic
            )
        ],
        states=_prepare_states(store=_check_phone_handlers),
        fallbacks=[
            CallbackQueryHandler(callback=ExitFallbackPhoneConvHandler.logic)
        ],
        name=f"conversation_{CommandEnum.CHECK_NUMBER.value}",
        allow_reentry=True,
        persistent=False,
    )

    conversation_instagram_check_handler = WrapConversationHandler(
        entry_points=[
            CommandHandler(
                CheckUsernameHandler.command, CheckUsernameHandler.logic
            )
        ],
        states=_prepare_states(store=_check_username_handlers),
        fallbacks=[
            CallbackQueryHandler(callback=ExitFallbackPhoneConvHandler.logic)
        ],
        name=f"conversation_{CommandEnum.CHECK_USERNAME.value}",
        allow_reentry=True,
        persistent=False,
    )

    conversation_link_check_handler = WrapConversationHandler(
        entry_points=[
            CommandHandler(
                StartCheckLinkHandler.command, StartCheckLinkHandler.logic
            )
        ],
        states=_prepare_states(store=_check_link_handlers),
        fallbacks=[],
        name=f"conversation_{CommandEnum.CHECK_LINK.value}",
        allow_reentry=True,
        persistent=False,
    )

    help_handler = CommandHandler(HelpHandler.command, HelpHandler.logic)

    # manager commands
    start_check_claim_handler = CommandHandler(
        StartCheckHandler.command, StartCheckHandler.logic
    )
    global_buttons_cb_handler = CallbackQueryHandler(
        GlobalButtonsCallbackHandler.logic
    )
    stat_total_handler = CommandHandler(
        TotalHandler.command, TotalHandler.logic
    )

    application.add_handlers(
        [
            conversation_instagram_check_handler,
            conversation_fetch_source_handler,
            conversation_phone_check_handler,
            conversation_link_check_handler,
            conversation_start_conv_handler,
            global_buttons_cb_handler,
            start_check_claim_handler,
            stat_total_handler,
            help_handler,
        ]
    )
