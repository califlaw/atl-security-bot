from src.core.enums import CommandEnum  # noqa
from src.core.wrap_handlers import WrapConversationHandler  # noqa

from .base import BaseHandlerKlass

# import impl klass commands
from .button_cb.klass import GlobalButtonsCallbackHandler
from .check_link.klass import (
    ParseLinkCheckProcessHandler,
    StartCheckLinkHandler,
)
from .check_number.klass import CheckNumberHandler, ParseCheckPhoneHandler
from .check_username.klass import (
    CheckUsernameHandler,
    ParseCheckUsernameHandler,
)
from .complain.klass import (
    ExitFallbackPhoneConvHandler,
    ParsePhoneOrLinkWithAskPlatformHandler,
    ParsePhotosOrStopConvHandler,
    ParsePlatformAskPhotosHandler,
    StartComplainHandler,
)
from .help.klass import HelpHandler
from .referral.klass import CallbackReferralConvHandler, StartReferralHandler
from .start.klass import (
    AskStartUserPhoneOrSkipHandler,
    ButtonStartCallbacksHandler,
    StartHandler,
)
from .start_check.klass import StartCheckHandler
from .total.klass import TotalHandler
