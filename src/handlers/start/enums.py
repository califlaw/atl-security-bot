from enum import Enum
from typing import Final

from telegram.ext import ConversationHandler


class HandlerStateEnum(Enum):
    AWAIT_PHONE: Final[int] = 0
    AWAIT_EMAIL: Final[int] = 1
    STOP_CONVERSATION: Final[int] = ConversationHandler.END
