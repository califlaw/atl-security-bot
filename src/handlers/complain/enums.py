from enum import Enum


class HandlerStateEnum(Enum):
    AWAIT_PHONE = 0
    AWAIT_PLATFORM = 1
    AWAIT_PHOTOS = 2
    STOP_CONVERSATION = 3
