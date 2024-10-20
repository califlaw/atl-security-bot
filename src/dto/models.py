from datetime import datetime
from pathlib import Path
from typing import List, Literal, Sequence
from uuid import UUID

from asyncpg import Record

from src.handlers.enums import StatusEnum


def create_record_class():
    base_class = Record

    def set_value(self, field_name, value):
        if field_name not in self.keys():
            raise KeyError(
                f"Field '{field_name}' does not exist in the record."
            )
        self._values[self._keys.index(field_name)] = value

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{item}'"
            )

    # Dynamically create a class with the added methods
    return type(
        "CustomRecord",
        (base_class,),
        {"set_value": set_value, "__getattr__": __getattr__},
    )


BaseRecord = create_record_class()


class Image(BaseRecord):
    id: UUID
    claim_id: int
    image_path: str | Path


class Claim(BaseRecord):
    id: int
    status: StatusEnum
    created_at: datetime
    type: Literal["phone", "link"]
    decision: str
    author: UUID
    link: str | None = None
    phone: str | None = None
    username: str | None = None
    images: Sequence[Image] = []


class Referrer(BaseRecord):
    id: int
    created_at: datetime
    author: UUID
    referrer_code: str
    referrers: List[int]


class Author(BaseRecord):
    id: UUID
    full_name: str
    tg_user_id: int
    tg_username: str
    email: str | None
