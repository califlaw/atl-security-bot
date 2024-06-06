from src.core.database import DBPool


class BaseDTO:
    _db: DBPool

    def __init__(self, db: DBPool):
        self._db = db
