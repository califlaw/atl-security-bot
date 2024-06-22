from enum import Enum, StrEnum


class HandlerStateEnum(Enum):
    CHOOSING = 0
    TYPING_REPLY = 1
    TYPING_CHOICE = 2


class StatusEnum(StrEnum):
    accepted = "accepted"
    pending = "pending"
    review = "review"
    resolved = "resolved"
    declined = "declined"


class TemplateFiles(StrEnum):
    help = "help"
    start = "start"
    total = "total"
    init_claim = "init_claim"
    start_check = "start_check"
