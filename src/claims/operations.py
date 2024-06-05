from typing import Dict

from src.core.database import DBPool
from src.handlers.states import StatusEnum


class Claim:
    _db: DBPool

    def __init__(self, db: DBPool):
        self._db = db

    async def initiation_claim(self, payload: Dict):
        return await self._db.execute_query(
            """
            insert into claims values ()
            """,
            params={},
        )

    async def set_status_claim(self, claim_id: int, status: StatusEnum):
        if status not in StatusEnum:
            raise KeyError(f'{status} not included key in StatusEnum')

        await self._db.execute_query(
            """
            update claims set status = %(status)s where id = %(id)
            """,
            params={'id': claim_id, 'status': status.value}
        )

    async def get_accepted_claim(self):
        return await self._db.execute_query(
            """
            select * from claims where status = 'accepted' 
            order by created_at limit 1
            """
        )

    async def resolve_claim(
        self, claim_id: int, decision: str, comment: str | None = None
    ):
        await self._db.execute_query(
            """
            update claims set comment = %(comment)s, 
            decision = %(decision)s where id = %(id)s
            """,
            params={"id": claim_id, "decision": decision, "comment": comment},
        )
        await self.set_status_claim(claim_id, status=StatusEnum.resolved)
