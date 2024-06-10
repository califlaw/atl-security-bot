from telegram import InlineKeyboardButton, Update
from telegram.ext import ContextTypes

from src.core.templates import render_template
from src.dto.claim import Claim
from src.handlers.mode import DEFAULT_PARSE_MODE
from src.keyboards.menu import make_reply_markup


async def start_bot_dialogs(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    claim = Claim(db=context.bot_data["database"])
    await claim.initiation_claim(payload={"comment": update.message.text})

    button_list = [
        InlineKeyboardButton("col1", callback_data=...),
        InlineKeyboardButton("col2", callback_data=...),
        InlineKeyboardButton("row 2", callback_data=...),
    ]

    await update.effective_chat.send_message(
        text=render_template("init_claim", mapping={"lol": "kek"}),
        parse_mode=DEFAULT_PARSE_MODE,
        reply_markup=make_reply_markup(button_list=button_list, colls=1),
    )
