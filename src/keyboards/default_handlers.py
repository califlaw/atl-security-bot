from typing import Dict

from telegram import BotCommandScopeDefault
from telegram.ext import Application, CommandHandler

users_commands: Dict[str, str] = {
    "help": "help",
    "start": "lolkek",
    "menu": "main menu with earning schemes",
}

admin_commands: Dict[str, str] = {
    "settings": "setting information about you",
}


async def set_default_commands(app: Application):
    remove_default_commands(app)

    for command, description in users_commands:
        app.add_handler(
            CommandHandler(command=command, description=description),
        )


def remove_default_commands(update: Application) -> None:
    update.remove_handler(scope=BotCommandScopeDefault())
