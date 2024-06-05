from telegram import Update
from telegram.ext import ContextTypes

from src.core.database import DBPool


async def start_bot_dialogs(update: Update, context: ContextTypes) -> None:
    # db = context.bot_data['database']  # type: DBPool
    # await db.execute_query()
    await update.effective_chat.send_message()
