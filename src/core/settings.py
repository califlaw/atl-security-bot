import configparser
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def _list_converter(value: str):
    return [i.strip() for i in value.split(",")]


settings = configparser.ConfigParser(converters={"list": _list_converter})
settings.read(os.path.join(BASE_DIR, "bot.config.ini"))
