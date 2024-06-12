from dataclasses import asdict, dataclass
from typing import Dict, List, Type

import structlog
from asyncpg import Record

from src.core.database import DBPool
from src.core.logger import log_event

logger = structlog.stdlib.get_logger(__name__)


@dataclass
class BaseDTO:
    db: DBPool

    def __init__(self, db: DBPool):
        self.db = db

    @staticmethod
    async def check_payload(required_fields: List[str], payload: Dict):
        """
        Checks if all the required fields are present in the payload.

        :param required_fields: A list of required fields (list of strings).
        :param payload: A dictionary containing data to be checked.
        :return: True if all required fields are present, otherwise False.
        """
        missing_fields = [
            field for field in required_fields if field not in payload
        ]

        if missing_fields:
            await log_event(
                logger=logger,
                message=f"Check missing fields. Missing fields:",
                payload={"fields": missing_fields},
            )
            return False

        return True

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_record(record: Record) -> "Type[Claim]":
        return record
