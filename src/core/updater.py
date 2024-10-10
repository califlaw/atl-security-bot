import asyncio
from typing import Any, Awaitable, Final, List

from telegram import Update, constants
from telegram.ext import SimpleUpdateProcessor

from src.core.settings import settings
from src.core.transliterate import R

ALL_ALLOWED_TYPES: Final[List[str]] = [
    constants.UpdateType.MESSAGE,
    constants.UpdateType.INLINE_QUERY,
    constants.UpdateType.CALLBACK_QUERY,
    constants.UpdateType.MY_CHAT_MEMBER,
    constants.UpdateType.CHAT_MEMBER,
    constants.UpdateType.CHOSEN_INLINE_RESULT,
]


class UpdProcessorMiddleware(SimpleUpdateProcessor):
    async def do_process_update(
        self,
        update: Update,
        coroutine: Awaitable[Any],
    ) -> None:
        if update.effective_chat.id == settings.getint("bot", "superGroupId"):
            # dont trigger bot updates on supergroup
            return

        R.string.set_language(language=update.effective_user.language_code)
        if coroutine and asyncio.iscoroutine(coroutine):
            await coroutine
