from typing import Dict, FrozenSet

import structlog
from telegram import (
    Bot,
    BotCommandScope,
    BotCommandScopeAllPrivateChats,
    BotCommandScopeChat,
    BotCommandScopeDefault,
)
from telegram.error import BadRequest
from telegram.ext import Application

from src.core.settings import settings
from src.core.transliterate import R

logger = structlog.stdlib.get_logger("keyboard.main")


class LanguageCommands:
    _allowed_langs: FrozenSet = {"en", "ru"}

    def formatting_commands(
        self, for_operators: bool = False
    ) -> Dict[str, Dict[str, str]]:
        result = {lang: {} for lang in self._allowed_langs}
        for _lang in self._allowed_langs:
            R.string.set_language(_lang)

            result[_lang].update(
                {
                    "help": R.string.ask_help,
                    "invitation": R.string.referral_query,
                    "start": R.string.start_claim_process,
                    "checknumber": R.string.checknumber_query,
                    "checkusername": R.string.checkusername_query,
                    "checklink": R.string.checklink_query,
                    "complain": R.string.complain_start,
                }
            )

            if for_operators:
                result[_lang].update(
                    {
                        "startcheck": R.string.startcheck_query,
                        "total": R.string.total_query,
                    }
                )

        return result


async def set_default_commands(_application: Application):
    _bot: Bot = _application.bot  # noqa
    l_commands = LanguageCommands()

    async def _remove_default_commands() -> None:
        await _bot.delete_my_commands(scope=BotCommandScopeDefault())

    async def _set_commands(
        lang_commands: Dict, scope: BotCommandScope | None = None
    ):
        for language_code, commands in lang_commands.items():
            await _bot.set_my_commands(
                commands=[
                    (command, description)
                    for (command, description) in commands.items()
                ],
                scope=scope,
                language_code=language_code,
            )

    await _remove_default_commands()

    for op_id in settings.getlist("bot", "operators", fallback=[]):  # type: int
        try:
            op = await _bot.get_chat(chat_id=op_id)
            await _set_commands(
                l_commands.formatting_commands(for_operators=True),
                scope=BotCommandScopeChat(chat_id=op.id),
            )
            await logger.ainfo(f"Operator commands set {op_id}")
        except BadRequest as e:
            await logger.ainfo(f"Chat not found for {op_id}: {e}")
            pass
    else:
        await _set_commands(
            l_commands.formatting_commands(),
            scope=BotCommandScopeAllPrivateChats(),
        )
