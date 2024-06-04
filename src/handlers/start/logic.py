from telegram import Update
from telegram.ext import ContextTypes


async def start_bot_dialogs(update: Update, context: ContextTypes) -> None:
    await update.effective_chat.send_message()
