from telegram import User

from src.dto.base import BaseDTO


class Author(BaseDTO):
    async def set_author(self, author: User):
        return await self.db.execute_query(
            """
            insert into author (id, full_name, tg_user_id) 
            values (gen_random_uuid(), '%(full_name)', '%(tg_id)s') 
            returning id;
            """,
            params={"tg_id": author.id, "full_name": author.name},
        )
