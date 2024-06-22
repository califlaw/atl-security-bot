import configparser
import os
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
BASE_DIR = Path(__file__).resolve().parent.parent.parent


def _list_converter(value: str):
    return [i.strip() for i in value.split(",")]


settings = configparser.ConfigParser(converters={"list": _list_converter})
settings.read(os.path.join(BASE_DIR, "bot.config.ini"))
