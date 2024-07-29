import re


def get_link(url: str) -> str | None:
    url_pattern = re.compile(
        r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|"
        r"[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    )
    _pattern_search = re.search(url_pattern, url)
    if not _pattern_search:
        return None

    return _pattern_search.groups()[0]
