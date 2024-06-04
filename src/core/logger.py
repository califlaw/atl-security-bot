import logging

import structlog

from src.core.settings import settings

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.getLevelName(settings.get("DEFAULT", "loggingLevel")),
)

logging.getLogger("httpx").setLevel(logging.WARNING)

logger = structlog.stdlib.get_logger(__name__)
