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
    is_general_group: bool = False,
    optional_text: str | None = None,
) -> AsyncGenerator[Claim | None, Bot]:
    bot = Bot(token=settings.get("bot", "token"))

    try:
        if claim and settings.getboolean(
            "bot", "notifyNewClaim", fallback=False
        ):
            params = {}
            if not is_general_group:
                params["message_thread_id"] = settings.getint(
                    "bot", "topicNotifyId"
                )

            await bot.send_message(
                chat_id=settings.get("bot", "superGroupId"),
                text=optional_text
                or render_template(TemplateFiles.alarm, mapping=claim),
                **params,
            )
    except (ChatMigrated, TelegramError, NoOptionError) as e:
        await logger.aexception("Telegram has sent error: %s", e)

    yield bot
