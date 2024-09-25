from enum import Enum
from typing import Any, Callable, Coroutine, Type

from telegram import Update
from telegram.ext import ContextTypes
from telegram.ext.filters import MessageFilter


class BaseHandlerKlass:
    command: str = ""
    is_query: bool = False
    state: Type[Enum] | None = None
    filters: Type[MessageFilter] | None = None
    logic: Callable[
        [Update, ContextTypes.DEFAULT_TYPE],
        Coroutine[Any, Any, None],
    ]
