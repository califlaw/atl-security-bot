from typing import Any, Callable, Coroutine

from telegram import Update
from telegram.ext import ContextTypes

from src.handlers.base import BaseHandlerKlass
from src.handlers.help.logic import help_callback


class HelpHandler(BaseHandlerKlass):
    command: str = "help"
    logic: Callable[
        [Update, ContextTypes.DEFAULT_TYPE],
        Coroutine[Any, Any, None],
    ] = help_callback
