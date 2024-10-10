from configparser import NoOptionError
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from telegram import Bot
from telegram.error import ChatMigrated, TelegramError

from src.core.settings import settings
from src.core.templates import render_template
from src.dto.models import Claim
from src.handlers.enums import TemplateFiles

logger = structlog.stdlib.get_logger("notify.bot")


@asynccontextmanager
async def notify_supergroup(
    claim: Claim | None = None,
) -> AsyncGenerator[Claim | None, Bot]:
    bot = Bot(token=settings.get("bot", "token"))

    try:
        if claim and settings.getboolean(
            "bot", "notifyNewClaim", fallback=False
        ):
            params = {}
            if topic_id := settings.getint(
                "bot", "topicNotifyId", fallback=None
            ):
                params["message_thread_id"] = topic_id

            await bot.send_message(
                chat_id=settings.get("bot", "superGroupId"),
                text=render_template(TemplateFiles.alarm, mapping=claim),
                **params,
            )
    except (ChatMigrated, TelegramError, NoOptionError) as e:
        await logger.aexception("Telegram has sent error: %s", e)

    yield bot
