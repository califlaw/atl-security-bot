import asyncio

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from src.core.database import DBPool
from src.core.settings import settings
from src.core.templates import init_templates
from src.handlers.registry import store
from src.keyboards.default_handlers import set_default_commands


async def post_init(_application: Application) -> None:
    await init_templates()
    _application.bot_data["database"] = await DBPool.init_db()
    await set_default_commands(_application=_application)


async def post_shutdown(_application: Application) -> None:
    await _application.bot_data["database"].close()


async def main():
    application = (
        Application.builder()
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .token(settings.get("bot", "token"))
        .build()
    )

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", lambda: None)],
        states={
            state: [MessageHandler(filters=None, callback=klass.logic)]
            for (state, klass) in store.items()
        },
        fallbacks=[MessageHandler(filters.Regex("^Done$"), lambda: None)],
        name="conversation",
        persistent=True,
    )
    application.add_handler(conversation_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    asyncio.run(main())
