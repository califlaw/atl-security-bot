from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from src.core.database import DBPool
from src.core.logger import set_default_params_log
from src.core.settings import settings
from src.handlers import StartHandler
from src.handlers.registry import store
from src.keyboards.default_handlers import set_default_commands


async def post_init(_application: Application) -> None:
    from src.core.templates import init_templates

    await init_templates()
    _application.bot_data["database"] = await DBPool().init_db()
    await set_default_commands(_application=_application)


async def post_shutdown(_application: Application) -> None:
    _db = _application.bot_data.get("database")
    if _db:
        await _db.close()


def main():
    # configure_logger(  # FIXME: catch correct logger
    #     enable_json_logs=settings.getboolean("DEFAULT", "jsonLog")
    # )
    set_default_params_log()

    application = (
        Application.builder()
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .token(settings.get("bot", "token"))
        .build()
    )

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", StartHandler.logic)],
        states={
            state: [MessageHandler(filters=None, callback=klass.logic)]
            for (state, klass) in store.items()
        },
        fallbacks=[MessageHandler(filters.Regex("^Done$"), lambda: None)],
        name="conversation",
        persistent=False,
    )
    application.add_handler(conversation_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
