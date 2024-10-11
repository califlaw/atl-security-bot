from enum import Enum
from typing import Final

from telegram.ext import ConversationHandler


class HandleCheckUsernameEnum(Enum):
    AWAIT_USERNAME: Final[int] = 0
    STOP_CONVERSATION: Final[int] = ConversationHandler.END
