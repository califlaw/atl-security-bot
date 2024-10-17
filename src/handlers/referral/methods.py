from telegram import CallbackQuery, Update, User
from telegram.ext import ContextTypes

from src.core.transliterate import R, effective_message
from src.core.utils import make_referral_link
from src.dto.referral import ReferralDTO


async def get_referral_link_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE, query: CallbackQuery
) -> None:
    bot: User = await context.bot.get_me()

    referral_obj = ReferralDTO(db=context.bot_data["database"])
    referral_code: str = (
        await referral_obj.initiation_referral(author=update.effective_user)
    ).referrer_code

    referral_link = make_referral_link(referral_code, bot.username)
    await effective_message(
        update,
        message=R.string.referral_link.format(referral_link),
        query=query,
    )


async def get_referral_positions_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE, query: CallbackQuery
) -> None:
    referral_obj = ReferralDTO(db=context.bot_data["database"])
    positions = await referral_obj.get_referral_positions(
        author=update.effective_user
    )

    await effective_message(
        update,
        message=R.string.referral_positions.format(positions),
        query=query,
    )
