from enum import Enum
from typing import Any, Callable, Coroutine, Type

from telegram import MessageEntity, Update
from telegram.ext import ContextTypes, filters
from telegram.ext.filters import MessageFilter

from src.core.enums import CommandEnum
from src.core.utils import simple_phone_regex
from src.handlers.base import BaseHandlerKlass
from src.handlers.start.enums import HandlerStateEnum
from src.handlers.start.logic import (
    query_start_button_cb_handler,
    start_callback,
)


class StartHandler(BaseHandlerKlass):
    command: str = CommandEnum.START.value
    logic: Callable[
        [Update, ContextTypes.DEFAULT_TYPE],
        Coroutine[Any, Any, int],
    ] = start_callback


# will use in future
class AskStartUserPhoneOrSkipHandler(BaseHandlerKlass):
    state: Type[Enum] | None = HandlerStateEnum.AWAIT_PHONE
    filters: Type[MessageFilter] | None = filters.Entity(
        MessageEntity.PHONE_NUMBER
    ) | filters.Regex(simple_phone_regex)
    logic: Callable[
        [Update, ContextTypes.DEFAULT_TYPE],
        Coroutine[Any, Any, int],
    ] = start_callback


class ButtonStartCallbacksHandler(BaseHandlerKlass):
    is_query: bool = True
    logic: Callable[
        [Update, ContextTypes.DEFAULT_TYPE],
        Coroutine[Any, Any, None],
    ] = query_start_button_cb_handler
