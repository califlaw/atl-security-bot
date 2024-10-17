from typing import Any, Callable, Coroutine

from telegram import Update
from telegram.ext import ContextTypes

from src.core.enums import CommandEnum
from src.handlers.base import BaseHandlerKlass
from src.handlers.referral.enums import HandlerStateEnum
from src.handlers.referral.logic import (
    referral_conversation_callback,
    referral_methods_callback,
)


class StartReferralHandler(BaseHandlerKlass):
    command: str = CommandEnum.REFERRAL.value
    logic: Callable[
        [Update, ContextTypes.DEFAULT_TYPE],
        Coroutine[Any, Any, int],
    ] = referral_conversation_callback


class CallbackReferralConvHandler(BaseHandlerKlass):
    state = HandlerStateEnum.AWAIT_ACTION
    is_query: bool = True
    logic: Callable[
        [Update, ContextTypes.DEFAULT_TYPE],
        Coroutine[Any, Any, int],
    ] = referral_methods_callback
