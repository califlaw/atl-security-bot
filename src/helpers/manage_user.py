from uuid import UUID

from telegram import Bot

from src.core.enums import AuthorRankEnum
from src.core.settings import settings
from src.helpers.notify_bot import notify_supergroup


async def promote_user(
    author_id: UUID,
    author_obj: "AuthorDTO",
    custom_title: AuthorRankEnum | str | None = None,
) -> bool:
    chat_id = settings.getint("bot", "moderateChatId", fallback=None)
    if not chat_id:
        return False

    user_id = (await author_obj.get_by_id(_id=author_id)).tg_user_id

    async with notify_supergroup() as bot:  # type: Bot
        await bot.promote_chat_member(
            chat_id,
            user_id,
            can_change_info=False,
            can_post_messages=False,
            can_edit_messages=False,
            can_delete_messages=False,
            can_invite_users=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_promote_members=False,
            is_anonymous=True,
            can_manage_chat=False,
            can_manage_video_chats=False,
            can_manage_topics=False,
            can_post_stories=False,
            can_edit_stories=False,
            can_delete_stories=False,
        )

        if custom_title:
            await bot.set_chat_administrator_custom_title(
                chat_id, user_id, custom_title=custom_title
            )

    return True
