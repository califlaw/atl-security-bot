from typing import Dict

import structlog
from telegram import (
    Bot,
    BotCommandScope,
    BotCommandScopeChat,
    BotCommandScopeDefault,
    ChatFullInfo,
)
from telegram.error import BadRequest
from telegram.ext import Application

from src.core.settings import settings

logger = structlog.stdlib.get_logger("keyboard.main")

user_commands: Dict[str, str] = {
    "help": "🆘 Получить помощь",
    "start": "🗃 Начать работу бота по заявкам",
    "checknumber": "📱Проверить номер телефона",
    "checklink": "🔗 Проверить ссылку",
    "complain": "💣 Пожаловаться на номер",
}

operator_commands: Dict[str, str] = {
    "startcheck": "👮🏼 Взять в обработку заявку",
    "total": "📊 Количество жалоб за все время",
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
    await _set_commands(user_commands)

    for operator in settings.getlist("bot", "operators", fallback=[]):
        try:
            op = await _application.bot.get_chat(operator)  # type: ChatFullInfo
            await _set_commands(
                operator_commands,
                scope=BotCommandScopeChat(chat_id=op.id),
            )
            logger.info(f"Operator commands set for {operator} (ID: {op.id}).")
        except BadRequest as e:
            pass
