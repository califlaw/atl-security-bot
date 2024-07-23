from typing import Any, Callable, Coroutine

from telegram import Update
from telegram.ext import ContextTypes

from src.handlers.base import BaseHandlerKlass
from src.handlers.complain.enums import HandlerStateEnum
from src.handlers.complain.logic import (
    complain_parse_phone_ask_platform_callback,
    complain_phone_callback,
)


class StartComplainHandler(BaseHandlerKlass):
    command: str = "complain"
    logic: Callable[
        [Update, ContextTypes.DEFAULT_TYPE],
        Coroutine[Any, Any, None],
    ] = complain_phone_callback


class ParsePhoneWithAskPlatformHandler(BaseHandlerKlass):
    command: str = ""
    state: HandlerStateEnum = HandlerStateEnum.AWAIT_PHONE
    logic: Callable[
        [Update, ContextTypes.DEFAULT_TYPE],
        Coroutine[Any, Any, None],
    ] = complain_parse_phone_ask_platform_callback
