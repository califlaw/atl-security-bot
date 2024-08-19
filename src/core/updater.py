from typing import Any, Awaitable

from telegram import Update
from telegram.ext import SimpleUpdateProcessor

from src.core.transliterate import R


class UpdProcessorMiddleware(SimpleUpdateProcessor):
    async def do_process_update(
        self,
        update: Update,
        coroutine: Awaitable[Any],
    ) -> None:
        R.string.set_language(language=update.effective_user.language_code)
        await coroutine
