from typing import Any, Callable, Coroutine, Type

from telegram import MessageEntity, Update
from telegram.ext import ContextTypes, filters
from telegram.ext.filters import MessageFilter

from src.core.utils import username_regex
from src.handlers.base import BaseHandlerKlass
from src.handlers.check_username.enums import HandleCheckUsernameEnum
from src.handlers.check_username.logic import (
    check_username_callback,
    start_check_username_callback,
)


class CheckUsernameHandler(BaseHandlerKlass):
    command: str = "checkusername"
    logic: Callable[
        [Update, ContextTypes.DEFAULT_TYPE],
        Coroutine[Any, Any, int],
    ] = start_check_username_callback


class ParseCheckUsernameHandler(BaseHandlerKlass):
    state: HandleCheckUsernameEnum = HandleCheckUsernameEnum.AWAIT_USERNAME
    filters: Type[MessageFilter] | None = filters.Entity(
        MessageEntity.MENTION
    ) & filters.Regex(username_regex)
    logic: Callable[
        [Update, ContextTypes.DEFAULT_TYPE],
        Coroutine[Any, Any, int],
    ] = check_username_callback
