from enum import Enum, StrEnum


class ExperienceEnum(Enum):
    newbie = 200
    advanced = 500
    expert = 1_000
    master = 2_000
    guru = 5_000
    legend = 10_000


class AuthorRankEnum(StrEnum):
    squire = "squire"
    warrior = "warrior"
    knight = "knight"
    commander = "commander"
    defender = "defender"
    legend = "legend"
