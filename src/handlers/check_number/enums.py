from enum import Enum
from typing import Final

from telegram.ext import ConversationHandler


class HandleCheckPhoneEnum(Enum):
    AWAIT_PHONE: Final[int] = 0
    STOP_CONVERSATION: Final[int] = ConversationHandler.END
