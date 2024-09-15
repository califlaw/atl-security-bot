from typing import Any, Callable, Coroutine

from telegram import Update
from telegram.ext import ContextTypes

from src.handlers.base import BaseHandlerKlass
from src.handlers.start_check.logic import start_manage_check_callback


class StartCheckHandler(BaseHandlerKlass):
    command: str = "startcheck"
    logic: Callable[
        [Update, ContextTypes.DEFAULT_TYPE],
        Coroutine[Any, Any, None],
    ] = start_manage_check_callback
