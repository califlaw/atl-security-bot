from typing import Callable

from telegram import Update
from telegram.ext import ContextTypes

from src.handlers.base import BaseHandlerKlass
from src.handlers.start.logic import start_bot_dialogs


class StartHandler(BaseHandlerKlass):
    command: str = "start"
    state = "start"
    logic: Callable[[Update, ContextTypes], None] = start_bot_dialogs
