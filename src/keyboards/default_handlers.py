from typing import Dict

from telegram import (
    Bot,
    BotCommandScope,
    BotCommandScopeChat,
    BotCommandScopeDefault,
)
from telegram.error import BadRequest
from telegram.ext import Application

from src.core.settings import settings

users_commands: Dict[str, str] = {
    "help": "🆘 Получить помощь",
    "start": "🗃 Начать работу бота по заявкам",
}

operator_commands: Dict[str, str] = {
    "check": "🕶 Взять в обработку заявку",
    "commit": "🎯 Внести комментарий и решение",
    "resolve": "✅ Завершить обработку заявки",
}


async def _remove_default_commands(_application: Application) -> None:
    await _application.bot.delete_my_commands(scope=BotCommandScopeDefault())


async def set_default_commands(_application: Application):
    async def _set_commands(
        commands: dict, scope: BotCommandScope | None = None
    ):
        await _application.bot.set_my_commands(  # type: Bot
            [
                (command, description)
                for (command, description) in commands.items()
            ],
            scope=scope,
        )

    await _remove_default_commands(_application)
    await _set_commands(users_commands)

    for operator_id in settings.getlist("bot", "operators"):
        try:
            await _set_commands(
                operator_commands,
                scope=BotCommandScopeChat(chat_id=operator_id),
            )
        except BadRequest:
            pass
