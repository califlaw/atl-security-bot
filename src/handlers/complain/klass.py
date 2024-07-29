from typing import Any, Callable, Coroutine

from telegram import Update
from telegram.ext import ContextTypes

from src.handlers.base import BaseHandlerKlass
from src.handlers.complain.enums import HandlerStateEnum
from src.handlers.complain.logic import (
    complain_parse_phone_or_link_ask_platform_callback,
    complain_parse_platform_ask_photos_callback,
    complain_phone_callback,
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
    logic: Callable[
        [Update, ContextTypes.DEFAULT_TYPE],
        Coroutine[Any, Any, int],
    ] = complain_parse_platform_ask_photos_callback
