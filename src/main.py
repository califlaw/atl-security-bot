from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from src.core.settings import settings
from src.core.templates import init_templates
from src.handlers.registry import store


async def main():
    await init_templates()
    application = Application.builder().token(settings.get("TOKEN")).build()

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
    main()
