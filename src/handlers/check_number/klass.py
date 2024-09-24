from typing import Any, Callable, Coroutine, Type

from telegram import MessageEntity, Update
from telegram.ext import ContextTypes, filters
from telegram.ext.filters import MessageFilter

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
        Coroutine[Any, Any, int],
    ] = start_check_phone_callback


class ParseCheckPhoneHandler(BaseHandlerKlass):
    command: str = ""
    state: HandleCheckPhoneEnum = HandleCheckPhoneEnum.AWAIT_PHONE
    filters: Type[MessageFilter] | None = filters.Entity(
        MessageEntity.PHONE_NUMBER
    ) | filters.Regex(r"^(0|7|8)\S+")
    logic: Callable[
        [Update, ContextTypes.DEFAULT_TYPE],
        Coroutine[Any, Any, int],
    ] = check_number_callback
