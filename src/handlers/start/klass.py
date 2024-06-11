from typing import Any, Callable, Coroutine

from telegram import Update
from telegram.ext import ContextTypes

from src.handlers.base import BaseHandlerKlass
from src.handlers.enums import HandlerStateEnum
from src.handlers.start.logic import start_callback


class StartHandler(BaseHandlerKlass):
    command: str = "start"
    state: HandlerStateEnum = HandlerStateEnum.CHOOSING
    logic: Callable[
        [Update, ContextTypes.DEFAULT_TYPE],
        Coroutine[Any, Any, None],
    ] = start_callback
