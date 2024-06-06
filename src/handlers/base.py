from typing import Callable

from telegram import Update
from telegram.ext import ContextTypes

from src.handlers.enums import HandlerStateEnum


class BaseHandlerKlass:
    command: str
    state: HandlerStateEnum
    logic: Callable[[Update, ContextTypes], None]
