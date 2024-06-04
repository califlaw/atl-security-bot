import configparser
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

settings = configparser.ConfigParser()
settings.read(os.path.join(BASE_DIR, "bot.config.ini"))
