from typing import Dict, List, Tuple

import structlog

from src.core.database import DBPool
from src.core.logger import log_event

logger = structlog.stdlib.get_logger(__name__)


class BaseDTO:
    db: DBPool

    def __init__(self, db: DBPool, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = db

    @staticmethod
    async def check_missed_payload(
        required_fields: List[str], payload: Dict
    ) -> Tuple[bool, List[str]]:
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
            return True, missing_fields

        return False, []
