from typing import Dict

from telegram import BotCommandScopeDefault
from telegram.ext import Application

users_commands: Dict[str, str] = {
    "help": "help",
    "start": "lolkek",
    "menu": "main menu with earning schemes",
}

admin_commands: Dict[str, str] = {
    "settings": "setting information about you",
}


async def set_default_commands(_application: Application):
    remove_default_commands(_application)

    _application.bot.set_my_commands(
        [
            (command, description)
            for (command, description) in users_commands.items()
        ]
    )


def remove_default_commands(_application: Application) -> None:
    _application.bot.set_my_commands(scope=BotCommandScopeDefault())
