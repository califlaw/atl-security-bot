from enum import Enum


class HandlerStateEnum(Enum):
    CHOOSING = 0
    TYPING_REPLY = 1
    TYPING_CHOICE = 2
