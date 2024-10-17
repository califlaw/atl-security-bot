import json
import os

import aiofiles
import structlog
from telegram import CallbackQuery, InlineKeyboardMarkup, Update
from telegram.helpers import escape_markdown

from src.core.logger import log_event
from src.core.settings import BASE_DIR

logger = structlog.stdlib.get_logger("transliterate")


class R:
    class _StringResource:
        _strings = {}
        _current_language = "ru"

        def __getattr__(self, name: str) -> str:
            strings: dict = self._strings.get(self._current_language, {})
            if name not in strings:
                raise AttributeError(
                    f"'R.string' has no attribute '{name}' "
                    f"in language '{self._current_language}'"
                )
            return strings[name]

        async def load_strings(self, language: str, file_path: str) -> None:
            async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                self._strings[language] = json.loads(await f.read())
            await log_event(
                logger,
                f"Loaded strings for '{language}': {self._strings[language]}",
            )

        def set_language(self, language: str) -> None:
            if language not in self._strings:
                raise ValueError(f"Language '{language}' not loaded")

            self._current_language = language

        def pluralize(self, name: str, count: int) -> str:
            strings = self._strings.get(self._current_language, {})
            if name in strings and isinstance(strings[name], dict):
                if count == 1:
                    return strings[name]["one"].format(count=count)
                elif 2 <= count <= 4:
                    return strings[name]["few"].format(count=count)
                else:
                    return strings[name]["many"].format(count=count)
            raise AttributeError(
                f"'R.string' has no plural forms for '{name}' "
                f"in language '{self._current_language}'"
            )

    string = _StringResource()


async def load_strings():
    for root, _, files in os.walk(os.path.join(BASE_DIR, "src", "resources")):
        for _trn_file in files:
            lang, _ = _trn_file.split(".")
            full_path = os.path.join(root, _trn_file)
            await R.string.load_strings(lang, full_path)


async def effective_message(
    update: Update,
    message: str,
    is_reply: bool = False,
    reply_markup: InlineKeyboardMarkup | None = None,
    query: CallbackQuery | None = None,
    **kwargs,
) -> None:
    text = escape_markdown(message, version=2, entity_type=None)

    if reply_markup:
        kwargs["reply_markup"] = reply_markup

    if query:
        await query.edit_message_text(text, **kwargs)
        return

    if is_reply:
        await update.message.reply_text(text=text, **kwargs)
    else:
        await update.effective_chat.send_message(text=text, **kwargs)
