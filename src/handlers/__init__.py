from .base import BaseHandlerKlass

# import impl klass commands
from .check_number.klass import CheckNumberHandler
from .check_link.klass import StartCheckLinkHandler
from .complain.klass import (
    ParsePhoneOrLinkWithAskPlatformHandler,
    ParsePhotosOrStopConvHandler,
    ParsePlatformAskPhotosHandler,
    StartComplainHandler,
)
from .help.klass import HelpHandler
from .start.klass import StartHandler
from .start_check.klass import StartCheckHandler
from .total.klass import TotalHandler
