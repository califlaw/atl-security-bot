from typing import Any, Callable, Coroutine, List, Type

from telegram import Update
from telegram.ext import ContextTypes, filters
from telegram.ext.filters import MessageFilter

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
    command: str = ""
    state: HandlerStateEnum = HandlerStateEnum.AWAIT_PHONE_OR_LINK
    logic: Callable[
        [Update, ContextTypes.DEFAULT_TYPE],
        Coroutine[Any, Any, int],
    ] = complain_parse_phone_or_link_ask_platform_callback


class ParsePlatformAskPhotosHandler(BaseHandlerKlass):
    command: str = ""
    state: HandlerStateEnum = HandlerStateEnum.AWAIT_PLATFORM
    logic: Callable[
        [Update, ContextTypes.DEFAULT_TYPE],
        Coroutine[Any, Any, int],
    ] = complain_parse_platform_ask_photos_callback


class ParsePhotosOrStopConvHandler(BaseHandlerKlass):
    command: str = ""
    state: HandlerStateEnum = HandlerStateEnum.AWAIT_PHOTOS
    filters: List[Type[MessageFilter]] | None = [filters.PHOTO | filters.VIDEO]
    logic: Callable[
        [Update, ContextTypes.DEFAULT_TYPE],
        Coroutine[Any, Any, int],
    ] = complain_parse_photos_or_stop_callback


class ExitFallbackPhoneConvHandler(BaseHandlerKlass):
    command: str = ""
    is_query: bool = True
    logic: Callable[
        [Update, ContextTypes.DEFAULT_TYPE],
        Coroutine[Any, Any, int],
    ] = fallback_exit_conv_callback
