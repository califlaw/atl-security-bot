import logging
import sys
from uuid import UUID

import orjson
import structlog
from structlog import BoundLogger

from src.core.settings import settings

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.getLevelName(settings.get("DEFAULT", "loggingLevel")),
    handlers=[logging.StreamHandler()],
)


def set_default_params_log():
    # Re-configure asyncio logger
    telegram_logger = logging.getLogger("telegram")
    telegram_logger.propagate = True
    telegram_logger.setLevel(logging.DEBUG)

    # Re-configure asyncio logger
    asyncio_logger = logging.getLogger("asyncio")
    asyncio_logger.propagate = False
    asyncio_logger.setLevel(logging.CRITICAL)

    # Re-configure httpx logger
    httpx_logger = logging.getLogger("httpx")
    httpx_logger.propagate = False
    httpx_logger.setLevel(logging.DEBUG)

    # Re-configure httpcore.http11 logger
    httpcore_logger = logging.getLogger("httpcore")
    httpcore_logger.propagate = False
    httpcore_logger.setLevel(logging.WARN)


def configure_logger(enable_json_logs: bool):
    timestamper = structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S")

    shared_processors = [
        timestamper,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.filter_by_level,
        structlog.processors.CallsiteParameterAdder(
            {
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.MODULE,
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.PROCESS,
                structlog.processors.CallsiteParameter.PROCESS_NAME,
            }
        ),
        structlog.stdlib.ExtraAdder(),
        structlog.processors.ExceptionRenderer(),
    ]

    structlog.configure(
        context_class=dict,
        processors=shared_processors  # type: ignore
        + [structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
        # call log with await syntax in thread pool executor
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    logs_render = (
        structlog.processors.JSONRenderer(serializer=orjson.dumps)
        if enable_json_logs
        else structlog.dev.ConsoleRenderer(colors=True)
    )

    _configure_default_logging_by_custom(shared_processors, logs_render)


def _configure_default_logging_by_custom(shared_processors, logs_render):
    handler = logging.StreamHandler(sys.stdout)

    # Use `ProcessorFormatter` to format all `logging` entries.
    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            _extract_from_record,
            logs_render,
        ],
    )

    handler.setFormatter(formatter)


def _extract_from_record(_, __, event_dict):
    # Extract thread and process names and add them to the event dict.
    event_dict.pop("_from_structlog", None)
    record = event_dict.pop("_record")
    event_dict["thread_name"] = record.threadName
    event_dict["process_name"] = record.processName
    return event_dict


async def log_event(
    logger: BoundLogger,
    message: str,
    level: int = logging.DEBUG,
    exc: Exception | None = None,
    client_id: UUID | None = None,
    payload: dict = None,
    **kwargs,
):
    if payload is None:
        payload = kwargs.get("payload", {})

    if not exc:
        await logger.alog(
            level=level,
            event=message,
            client_id=str(client_id),
            payload=payload,
            params=kwargs,
        )
    else:
        await logger.exception(message, exc)  # type: ignore
