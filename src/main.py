import pytz
import sentry_sdk
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.asyncpg import AsyncPGIntegration
from sentry_sdk.integrations.httpx import HttpxIntegration
from telegram.constants import ParseMode
from telegram.ext import Application, Defaults

from src.core.database import DBPool
from src.core.logger import set_default_params_log
from src.core.settings import local_app, settings
from src.core.transliterate import load_strings
from src.core.updater import ALL_ALLOWED_TYPES, UpdProcessorMiddleware
from src.handlers.registry import registration_handlers
from src.keyboards.default_handlers import set_default_commands


async def post_init(_application: Application) -> None:
    from src.core.templates import init_templates

    if sentry_dsn := settings.get("DEFAULT", "sentryDsn"):
        _env = settings.get("DEFAULT", "environment", fallback="dev")
        sentry_sdk.init(
            dsn=sentry_dsn,
            environment=_env,
            sample_rate=1.0,
            profiles_sample_rate=1.0,
            integrations=[
                HttpxIntegration(),
                AsyncPGIntegration(),
                AsyncioIntegration(),
            ],
        )

    await load_strings()
    await init_templates()
    _application.bot_data["database"] = await DBPool().init_db()
    await set_default_commands(_application=_application)


async def post_shutdown(_application: Application) -> None:
    if _db_connector := _application.bot_data.get("database"):
        await _db_connector.close()


def main():
    # configure_logger(  # FIXME: catch correct logger
    #     enable_json_logs=settings.getboolean("DEFAULT", "jsonLog")
    # )
    set_default_params_log()
    defaults = Defaults(
        parse_mode=ParseMode.MARKDOWN_V2,
        tzinfo=pytz.timezone(settings.get("DEFAULT", "timezone")),
    )

    upd_processor = UpdProcessorMiddleware(
        max_concurrent_updates=settings.getint("bot", "max_concurrent")
    )

    application = (
        Application.builder()
        .defaults(defaults)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .concurrent_updates(upd_processor)
        .token(settings.get("bot", "token"))
        .build()
    )
    local_app.app = application

    # registration logic commands
    registration_handlers(application=application)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=ALL_ALLOWED_TYPES)


if __name__ == "__main__":
    main()
