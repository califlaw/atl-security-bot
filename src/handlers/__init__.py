from .base import BaseHandlerKlass
from .check_link.klass import CheckLinkHandler

# import impl klass commands
from .complain.klass import (
    ParsePhoneWithAskPlatformHandler,
    StartComplainHandler,
)
from .help.klass import HelpHandler
from .start.klass import StartHandler
from .start_check.klass import StartCheckHandler
from .total.klass import TotalHandler
