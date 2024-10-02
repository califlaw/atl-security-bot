from enum import Enum
from typing import Final

from telegram.ext import ConversationHandler


class HandleCheckLinkEnum(Enum):
    AWAIT_LINK: Final[int] = 0
    STOP_CONVERSATION: Final[int] = ConversationHandler.END
