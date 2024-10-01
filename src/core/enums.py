from enum import Enum, StrEnum


class ExperienceEnum(Enum):
    simple = 100
    modern = 300
    advanced = 500


class AuthorRankEnum(StrEnum):
    beginner = "beginner"
    advanced = "advanced"
    pro = "pro"
