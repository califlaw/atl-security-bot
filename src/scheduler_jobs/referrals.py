from telegram.ext import ContextTypes

from src.dto.referral import ReferralDTO
from src.helpers.notify_bot import notify_supergroup


async def top_referrals_callback(context: ContextTypes.DEFAULT_TYPE):
    referral_obj: ReferralDTO = ReferralDTO(db=context.bot_data["database"])
    ranked_users = await referral_obj.get_ranked_users()
    text = "Топы пришлашенных\n\n"

    for index, ranked_user in enumerate(ranked_users, start=1):
        text += f"{index} место: {ranked_user.get("username")} \n"

    async with notify_supergroup(is_general_group=True, text=text):
        pass
