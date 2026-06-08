
from contextvars import ContextVar

from dataclasses import dataclass

from typing import NewType

from aiogram import Bot


@dataclass
class Objects:
    menu_message_id: int | None = None
    last_message_id: int | None = None


@dataclass(frozen=True)
class _Typing:
    BotId = NewType("BotId", int)
    UserId = NewType("UserId", int)
    ChatId = NewType("ChatId", int)
    ThreadId = NewType("ThreadId", int)


@dataclass(frozen=True)
class Binding(_Typing):
    bot_id: _Typing.BotId
    user_id: _Typing.UserId
    chat_id: _Typing.ChatId
    thread_id: _Typing.ThreadId


@dataclass(frozen=True)
class Metadata(Binding):
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    user_str: str | None = None


@dataclass(frozen=True)
class Control:
    bot: Bot
    chat_id: int
    user_id: int
    thread_id: int | None
    flow: Objects


binding_var: ContextVar[Binding | None] = ContextVar("binding_var", default=None)
