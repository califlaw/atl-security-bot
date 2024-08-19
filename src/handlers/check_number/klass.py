from typing import Any, Callable, Coroutine

from telegram import Update
from telegram.ext import ContextTypes

from src.handlers.base import BaseHandlerKlass
from src.handlers.check_number.enums import HandleCheckPhoneEnum
from src.handlers.check_number.logic import (
    check_number_callback,
    start_check_phone_callback,
)


class CheckNumberHandler(BaseHandlerKlass):
    command: str = "checknumber"
    logic: Callable[
        [Update, ContextTypes.DEFAULT_TYPE],
        Coroutine[Any, Any, None],
    ] = start_check_phone_callback


class ParseCheckPhoneHandler(BaseHandlerKlass):
    command: str = ""
    state: HandleCheckPhoneEnum = HandleCheckPhoneEnum.AWAIT_PHONE
    logic: Callable[
        [Update, ContextTypes.DEFAULT_TYPE],
        Coroutine[Any, Any, None],
    ] = check_number_callback
