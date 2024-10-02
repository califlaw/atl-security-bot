from enum import Enum
from typing import Final

from telegram.ext import ConversationHandler


class HandlerStateEnum(Enum):
    AWAIT_PHONE_OR_LINK: Final[int] = 0
    AWAIT_PLATFORM: Final[int] = 1
    AWAIT_PHOTOS: Final[int] = 2
    STOP_CONVERSATION: Final[int] = ConversationHandler.END
