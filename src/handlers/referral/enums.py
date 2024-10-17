from enum import Enum, StrEnum
from typing import Final

from telegram.ext import ConversationHandler


class HandlerStateEnum(Enum):
    AWAIT_ACTION: Final[int] = 0
    STOP_CONVERSATION: Final[int] = ConversationHandler.END


class CallbackDataEnum(StrEnum):
    GET_REFERRAL_LINK = "getreferrallink"
    GET_REFERRAL_POSITION = "getreferralposition"
