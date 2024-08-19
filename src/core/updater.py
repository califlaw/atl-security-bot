from typing import Any, Awaitable, Final, List

from telegram import Update, constants
from telegram.ext import SimpleUpdateProcessor

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
        R.string.set_language(language=update.effective_user.language_code)
        await coroutine
