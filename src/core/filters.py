from re import Pattern, RegexFlag, compile

from telegram.ext.filters import Regex


class FlagPatternRegex(Regex):
    def __init__(
        self,
        pattern: str | Pattern[str],
        flags: int | RegexFlag = RegexFlag.NOFLAG,
    ):
        if isinstance(pattern, str):
            pattern = compile(pattern, flags=flags)
        self.pattern: Pattern[str] = pattern
        super().__init__(pattern=pattern)
