from typing import Any, Callable, Coroutine

from telegram import Update
from telegram.ext import ContextTypes

from src.handlers import BaseHandlerKlass
from src.handlers.button_cb.logic import button_callback


class ButtonCallbacksHandler(BaseHandlerKlass):
    command: str = ""
    is_query: bool = True
    logic: Callable[
        [Update, ContextTypes.DEFAULT_TYPE],
        Coroutine[Any, Any, None],
    ] = button_callback
