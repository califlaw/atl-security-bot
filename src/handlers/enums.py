from enum import StrEnum


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
    start_check = "start_check"
    check_claim = "check_claim"
