from typing import Any, Callable, Coroutine

from telegram import Update
from telegram.ext import ContextTypes

from src.handlers.base import BaseHandlerKlass
from src.handlers.enums import HandlerStateEnum
from src.handlers.start_check.logic import check_callback


class StartCheckHandler(BaseHandlerKlass):
    command: str = "startcheck"
    state: HandlerStateEnum = HandlerStateEnum.CHOOSING
    logic: Callable[
        [Update, ContextTypes.DEFAULT_TYPE],
        Coroutine[Any, Any, None],
    ] = check_callback
