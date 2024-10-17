from telegram import InlineKeyboardButton, Update
from telegram.ext import ContextTypes

from src.core.transliterate import R, effective_message
from src.handlers.referral.enums import CallbackDataEnum, HandlerStateEnum
from src.handlers.referral.methods import (
    get_referral_link_callback,
    get_referral_positions_callback,
)
from src.keyboards.menu import make_reply_markup


async def referral_methods_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    query = update.callback_query
    await query.answer()
    callback_data: CallbackDataEnum = query.data  # noqa

    if callback_data == CallbackDataEnum.GET_REFERRAL_LINK.value:
        await get_referral_link_callback(update, context, query)
    elif callback_data == CallbackDataEnum.GET_REFERRAL_POSITION.value:
        await get_referral_positions_callback(update, context, query)
    else:
        return HandlerStateEnum.STOP_CONVERSATION.value

    return HandlerStateEnum.STOP_CONVERSATION.value


async def referral_conversation_callback(update: Update, _) -> int:
    button_list = [
        InlineKeyboardButton(
            text=R.string.referral_link_option,
            callback_data=CallbackDataEnum.GET_REFERRAL_LINK.value,
        ),
        InlineKeyboardButton(
            text=R.string.referral_position_option,
            callback_data=CallbackDataEnum.GET_REFERRAL_POSITION.value,
        ),
    ]

    await effective_message(
        update,
        message=R.string.select_option,
        reply_markup=make_reply_markup(button_list=button_list),
    )

    return HandlerStateEnum.AWAIT_ACTION.value
