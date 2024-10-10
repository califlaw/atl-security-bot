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
    alarm = "alarm"
    start_check = "start_check"
    registered_user = "registered_user"
    check_link_claim = "check_link_claim"
    check_phone_claim = "check_phone_claim"
