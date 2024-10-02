from re import RegexFlag
from typing import Any, Callable, Coroutine, Type

from telegram import MessageEntity, Update
from telegram.ext import ContextTypes, filters
from telegram.ext.filters import MessageFilter

from src.core.filters import FlagPatternRegex
from src.core.utils import url_regex
from src.handlers.base import BaseHandlerKlass
from src.handlers.check_link.enums import HandleCheckLinkEnum
from src.handlers.check_link.logic import (
    parse_link_process_callback,
    start_check_link_callback,
)


class StartCheckLinkHandler(BaseHandlerKlass):
    command: str = "checklink"
    logic: Callable[
        [Update, ContextTypes.DEFAULT_TYPE],
        Coroutine[Any, Any, int],
    ] = start_check_link_callback


class ParseLinkCheckProcessHandler(BaseHandlerKlass):
    filters: Type[MessageFilter] | None = (
        filters.TEXT
        & filters.Entity(MessageEntity.URL)
        & FlagPatternRegex(url_regex, flags=RegexFlag.IGNORECASE)
    )
    state: HandleCheckLinkEnum = HandleCheckLinkEnum.AWAIT_LINK
    logic: Callable[
        [Update, ContextTypes.DEFAULT_TYPE],
        Coroutine[Any, Any, int],
    ] = parse_link_process_callback
