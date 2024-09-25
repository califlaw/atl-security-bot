import asyncio
import base64
import random
import re
import string
from asyncio import AbstractEventLoop, Task
from typing import Any, Callable, Coroutine, Dict

from orjson import orjson
from telegram import Bot
from telegram.constants import ChatAction

simple_phone_regex = r"^(0|7|8)\d+"
url_regex = (
    r"^(https?|ftp)://"
    r"([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,6}"
    r"(:\d+)?"
    r"(/[-a-zA-Z0-9@:%._+~#=]*)*"
    r"(\?[;&a-zA-Z0-9%_.,~+=-]*)?"
    r"(#[-a-zA-Z0-9_]*)?$"
)


def unpack_args(args):
    return {
        key: value
        for key, value in (
            args.items() if isinstance(args, dict) else args[0].items()
        )
    }


def async_partial(
    f: Callable, *args
) -> Callable[[], Coroutine[Any, Any, Any]]:
    async def f2():
        result = f(**unpack_args(*args))
        if asyncio.iscoroutinefunction(f):
            result = await result
        return result

    return f2


def random_string(length: int) -> str:
    return "".join(
        random.choices(string.ascii_uppercase + string.digits, k=length)
    )


def decode_url_b64(link: str) -> str:
    return base64.urlsafe_b64encode(link.encode()).decode().strip("=")


def serialize_orjson(content: Any) -> bytes:
    return orjson.dumps(
        content,
        option=(
            orjson.OPT_NON_STR_KEYS
            | orjson.OPT_SERIALIZE_UUID
            | orjson.OPT_SERIALIZE_DATACLASS
        ),
    )


def get_link(url: str) -> str | None:
    url_pattern = re.compile(pattern=url_regex)
    _pattern_search = re.match(url_pattern, url)
    if not _pattern_search:
        return None

    return _pattern_search.group()


async def create_bg_task(
    coro: Coroutine,
    cb: Callable,
    ctx: Dict,
    loop: AbstractEventLoop | None = None,
) -> None:
    _loop = loop or asyncio.get_event_loop()

    _name_task = f"background-task-{random_string(length=6)}"
    task: Task = _loop.create_task(coro, name=_name_task)

    async def wrapped_cb(res: Task) -> None:
        ctx.update({"task_result": res.result()})
        await asyncio.sleep(0)  # switch context to coroutine
        func: Callable[[], Coroutine[Any, Any, Any]] = async_partial(cb, ctx)
        await func()

    task.add_done_callback(lambda res: asyncio.create_task(wrapped_cb(res)))
    await asyncio.shield(task)


class ChatActionContext:
    def __init__(self, bot, chat_id, action: str = ChatAction.TYPING.value):
        self.bot: Bot = bot
        self.action: str = action
        self.chat_id: int = chat_id

    async def __aenter__(self):
        await self.bot.send_chat_action(
            chat_id=self.chat_id, action=self.action
        )
        await asyncio.sleep(0.5)
        return self.bot

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
