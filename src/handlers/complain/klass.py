from typing import Any, Callable, Coroutine

from telegram import Update
from telegram.ext import ContextTypes

from src.handlers.base import BaseHandlerKlass
from src.handlers.complain.logic import complain_phone_callback
from src.handlers.enums import HandlerStateEnum


class ComplainHandler(BaseHandlerKlass):
    command: str = "complain"
    is_query: bool = True
    state: HandlerStateEnum = HandlerStateEnum.CHOOSING
    logic: Callable[
        [Update, ContextTypes.DEFAULT_TYPE],
        Coroutine[Any, Any, None],
    ] = complain_phone_callback
