from typing import Any, Callable, Coroutine, Type

from telegram import Update
from telegram.ext import ContextTypes
from telegram.ext.filters import BaseFilter

from src.handlers.enums import HandlerStateEnum


class BaseHandlerKlass:
    command: str
    is_query: bool = False
    state: HandlerStateEnum | None = None
    filters: Type[BaseFilter] | None = None
    logic: Callable[
        [Update, ContextTypes.DEFAULT_TYPE],
        Coroutine[Any, Any, None],
    ]
