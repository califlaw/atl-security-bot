import configparser
import os
from functools import lru_cache
from pathlib import Path

from telegram.ext import Application


class LocalApp:
    _app: Application | None = None

    @property
    def app(self) -> Application:
        return self._app

    @app.setter
    def app(self, app):
        self._app = app


local_app = LocalApp()
settings: configparser.ConfigParser
BASE_DIR = Path(__file__).resolve().parent.parent.parent


def _list_converter(value: str):
    return [i.strip() for i in value.split(",")]


@lru_cache
def init_settings():
    global settings
    settings = _cfg = configparser.ConfigParser(
        converters={"list": _list_converter}
    )
    _cfg.read(os.path.join(BASE_DIR, "bot.config.ini"))

    return settings


settings = init_settings()
