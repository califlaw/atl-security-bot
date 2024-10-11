from re import RegexFlag
from typing import Any, Callable, Coroutine, Type

from telegram import MessageEntity, Update
from telegram.ext import ContextTypes, filters
from telegram.ext.filters import MessageFilter

from src.core.filters import FlagPatternRegex
from src.core.utils import simple_phone_regex, url_regex, username_regex
from src.handlers.base import BaseHandlerKlass
from src.handlers.complain.enums import HandlerStateEnum
from src.handlers.complain.logic import (
    complain_parse_phone_or_link_ask_platform_callback,
    complain_parse_photos_or_stop_callback,
    complain_parse_platform_ask_photos_callback,
    complain_phone_callback,
    fallback_exit_conv_callback,
)


class StartComplainHandler(BaseHandlerKlass):
    command: str = "complain"
    logic: Callable[
        [Update, ContextTypes.DEFAULT_TYPE],
        Coroutine[Any, Any, None],
    ] = complain_phone_callback


class ParsePhoneOrLinkWithAskPlatformHandler(BaseHandlerKlass):
    state: HandlerStateEnum = HandlerStateEnum.AWAIT_PHONE_OR_LINK
    filters: Type[MessageFilter] | None = (
        (
            filters.Entity(MessageEntity.PHONE_NUMBER)  # international format
            | filters.Regex(simple_phone_regex)
        )
        | (
            filters.Entity(MessageEntity.MENTION)
            & FlagPatternRegex(username_regex, flags=RegexFlag.IGNORECASE)
        )
        | (
            filters.Entity(MessageEntity.URL)
            & FlagPatternRegex(url_regex, flags=RegexFlag.IGNORECASE)
        )
    )
    logic: Callable[
        [Update, ContextTypes.DEFAULT_TYPE],
        Coroutine[Any, Any, int],
    ] = complain_parse_phone_or_link_ask_platform_callback


class ParsePlatformAskPhotosHandler(BaseHandlerKlass):
    state: HandlerStateEnum = HandlerStateEnum.AWAIT_PLATFORM
    logic: Callable[
        [Update, ContextTypes.DEFAULT_TYPE],
        Coroutine[Any, Any, int],
    ] = complain_parse_platform_ask_photos_callback


class ParsePhotosOrStopConvHandler(BaseHandlerKlass):
    state: HandlerStateEnum = HandlerStateEnum.AWAIT_PHOTOS
    filters: Type[MessageFilter] | None = (
        filters.PHOTO | filters.Document.IMAGE
    )
    logic: Callable[
        [Update, ContextTypes.DEFAULT_TYPE],
        Coroutine[Any, Any, int],
    ] = complain_parse_photos_or_stop_callback


class ExitFallbackPhoneConvHandler(BaseHandlerKlass):
    is_query: bool = True
    logic: Callable[
        [Update, ContextTypes.DEFAULT_TYPE],
        Coroutine[Any, Any, int],
    ] = fallback_exit_conv_callback
