from typing import Dict

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

logger = structlog.stdlib.get_logger("keyboard.main")

user_commands: Dict[str, str] = {
    "help": "🆘 Получить помощь",
    "start": "🗃 Начать работу бота по заявкам",
    "checknumber": "📱Проверить номер телефона",
    "checklink": "🔗 Проверить ссылку",
    "complain": "💣 Пожаловаться на номер",
}

operator_commands: Dict[str, str] = {
    "startcheck": "👮 Взять заявку в обработку",
    "total": "📊 Количество жалоб за все время",
}


async def set_default_commands(_application: Application):
    _bot: Bot = _application.bot

    async def _remove_default_commands() -> None:
        await _bot.delete_my_commands(scope=BotCommandScopeDefault())

    async def _set_commands(
        commands: Dict, scope: BotCommandScope | None = None
    ):
        await _bot.set_my_commands(
            commands=[
                (command, description)
                for (command, description) in commands.items()
            ],
            scope=scope,
        )

    await _remove_default_commands()
    await _set_commands(user_commands, scope=BotCommandScopeAllPrivateChats())

    for op_id in settings.getlist("bot", "operators", fallback=[]):  # type: int
        try:
            op = await _bot.get_chat(chat_id=op_id)
            await _set_commands(
                # both commands of user and operators,
                # cause operator could make new claim
                {**user_commands, **operator_commands},
                scope=BotCommandScopeChat(chat_id=op.id),
            )
            await logger.ainfo(f"Operator commands set {op_id}")
        except BadRequest as e:
            await logger.ainfo(f"Chat not found for {op_id}: {e}")
            pass
