from .base import BaseHandlerKlass

# import impl klass commands
from .button_cb.klass import ButtonCallbacksHandler
from .check_link.klass import (
    ParseLinkCheckProcessHandler,
    StartCheckLinkHandler,
)
from .check_number.klass import CheckNumberHandler, ParseCheckPhoneHandler
from .complain.klass import (
    ExitFallbackPhoneConvHandler,
    ParsePhoneOrLinkWithAskPlatformHandler,
    ParsePhotosOrStopConvHandler,
    ParsePlatformAskPhotosHandler,
    StartComplainHandler,
)
from .help.klass import HelpHandler
from .start.klass import StartHandler
from .start_check.klass import StartCheckHandler
from .total.klass import TotalHandler
