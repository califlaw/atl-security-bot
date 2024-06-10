from dataclasses import asdict, dataclass
from typing import Type

from asyncpg import Record

from src.core.database import DBPool


@dataclass
class BaseDTO:
    db: DBPool

    def __init__(self, db: DBPool):
        self.db = db

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_record(record: Record) -> "Type[Claim]":
        return record
