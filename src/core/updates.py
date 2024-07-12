from typing import List, Final

from telegram import constants

ALL_ALLOWED_TYPES: Final[List[str]] = [
    constants.UpdateType.MESSAGE,
    constants.UpdateType.INLINE_QUERY,
    constants.UpdateType.CALLBACK_QUERY,
    constants.UpdateType.MY_CHAT_MEMBER,
    constants.UpdateType.CHAT_MEMBER,
    constants.UpdateType.CHOSEN_INLINE_RESULT,
]
