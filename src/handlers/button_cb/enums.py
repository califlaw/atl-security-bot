from enum import StrEnum


class CallbackStateEnum(StrEnum):
    resolve = "resolve"
    decline = "decline"
    skip_photos = "skip_photos"
