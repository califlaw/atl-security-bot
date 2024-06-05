from typing import Dict

from telegram import (
    BotCommandScope,
    BotCommandScopeChat,
    BotCommandScopeDefault,
)
from telegram.ext import Application

from src.core.settings import settings

users_commands: Dict[str, str] = {
    "help": "help",
    "start": "lolkek",
    "menu": "main menu with earning schemes",
}

admin_commands: Dict[str, str] = {
    "settings": "setting information about you",
}


async def _remove_default_commands(_application: Application) -> None:
    await _application.bot.delete_my_commands(scope=BotCommandScopeDefault())


async def set_default_commands(_application: Application):
    async def _set_commands(
        commands: dict, scope: BotCommandScope | None = None
    ):
        await _application.bot.set_my_commands(
            [
                (command, description)
                for (command, description) in commands.items()
            ],
            scope=scope,
        )

    await _remove_default_commands(_application)
    await _set_commands(users_commands)

    for admin_id in settings.getlist("bot", "admins"):
        await _set_commands(
            admin_commands, scope=BotCommandScopeChat(chat_id=admin_id)
        )
