from enum import Enum, StrEnum


class ExperienceEnum(Enum):
    invite_people = 50
    processing_claim = 50
    publish_story = 100
    email = 100


class AuthorRankEnum(StrEnum):
    squire = "squire"
    warrior = "warrior"
    knight = "knight"
    commander = "commander"
    defender = "defender"
    legend = "legend"


class CommandEnum(StrEnum):
    COMPLAIN = "complain"
    CHECK_NUMBER = "checknumber"
    CHECK_LINK = "checklink"
    CHECK_USERNAME = "checkusername"
    START = "start"
    REFERRAL = "invitation"
