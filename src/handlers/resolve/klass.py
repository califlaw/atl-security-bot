from typing import Any, Callable, Coroutine

from telegram import Update
from telegram.ext import ContextTypes

from src.handlers.base import BaseHandlerKlass
from src.handlers.enums import HandlerStateEnum
from src.handlers.resolve.logic import resolve_callback


class ResolveHandler(BaseHandlerKlass):
    command: str = "resolve"
    state: HandlerStateEnum = HandlerStateEnum.TYPING_REPLY
    logic: Callable[
        [Update, ContextTypes.DEFAULT_TYPE],
        Coroutine[Any, Any, None],
    ] = resolve_callback
