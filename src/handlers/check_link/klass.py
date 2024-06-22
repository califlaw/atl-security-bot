from typing import Any, Callable, Coroutine

from telegram import Update
from telegram.ext import ContextTypes

from src.handlers.base import BaseHandlerKlass
from src.handlers.check_link.logic import check_callback
from src.handlers.enums import HandlerStateEnum


class CheckLinkHandler(BaseHandlerKlass):
    command: str = "checklink"
    state: HandlerStateEnum = HandlerStateEnum.CHOOSING
    logic: Callable[
        [Update, ContextTypes.DEFAULT_TYPE],
        Coroutine[Any, Any, None],
    ] = check_callback
