
from abc import ABC, abstractmethod

from contextlib import suppress

from dataclasses import dataclass

from aiogram.exceptions import TelegramForbiddenError
from aiogram.exceptions import TelegramMigrateToChat

from aiogram.types import TelegramObject
from aiogram.types import ResultChatMemberUnion
from aiogram.types import ChatFullInfo
from aiogram.types import User
from aiogram.types import Chat
from aiogram import Bot

from tgable.metadata import Objects
from tgable.metadata import Control
from tgable.metadata import Binding
from tgable.metadata import Metadata

from tgable.payload import Payload
from tgable.limiter import Limiter
from tgable.channel import Channel


@dataclass(frozen=True)
class RequestDetails:
    self_details: User
    chat_members: int
    chat_details: ChatFullInfo | None
    chat_options: ResultChatMemberUnion | None
    user_options: ResultChatMemberUnion | None


def user_str_from_user(user: User) -> str:
    # if message.forward_from_chat is not None:
    #     return "extra-" + message.forward_from_chat.username
    if user.username:
        return user.username
    if user.first_name and user.last_name:
        return user.first_name + " " + user.last_name
    if user.first_name or user.last_name:
        return (user.first_name or "") + (user.last_name or "")

    return "#" + str(user.id)


@dataclass(frozen=True)
class Request[PayloadT: Payload]:
    metadata: Metadata
    details: RequestDetails
    payload: PayloadT
    as_event: TelegramObject


class Parsing[TelegramObjectT: TelegramObject](ABC):

    def __init__(self, event: TelegramObjectT) -> None:
        self._event: TelegramObjectT = event
        self._details: RequestDetails | None = None

    @property
    @abstractmethod
    def _object_id(self) -> str:
        ...

    @property
    def as_text(self) -> str:
        clsname = self.__class__.__name__
        if not clsname.endswith("Parsing"):
            raise ValueError
        clsname = clsname.removesuffix("Parsing").lower()
        return f"{clsname}={self._object_id}"

    @property
    @abstractmethod
    def _flow(self) -> Objects:
        ...

    @property
    @abstractmethod
    def _user(self) -> User:
        ...

    @property
    def _user_id(self) -> int:
        if self._chat_id > 0:
            return self._chat_id
        return self._user.id

    @property
    @abstractmethod
    def _chat(self) -> Chat | None:
        ...

    @property
    def _chat_id(self) -> int:
        if self._chat is None:
            return self._user.id
        return self._chat.id

    @property
    @abstractmethod
    def _thread_id(self) -> int | None:
        ...

    @property
    def _bot(self) -> Bot:
        assert self._event.bot is not None
        return self._event.bot

    @property
    def _metadata(self) -> Metadata:
        return Metadata(
            bot_id=Binding.BotId(self._bot.id),
            user_id=Binding.UserId(self._user_id),
            chat_id=Binding.ChatId(self._chat_id),
            thread_id=Binding.ThreadId(self._thread_id or 0),
            first_name=self._user.first_name,
            last_name=self._user.last_name,
            username=self._user.username,
            user_str=user_str_from_user(self._user),
        )

    @property
    def binding(self) -> Binding:
        return self._metadata

    @property
    def _control(self) -> Control:
        return Control(
            bot=self._bot,
            chat_id=self._chat_id,
            user_id=self._user_id,
            thread_id=self._thread_id,
            flow=self._flow,
        )

    def channel(self, limiter: Limiter) -> Channel:
        return Channel(limiter, self._control)

    async def details(self) -> RequestDetails:

        if self._details is None:

            self_details = await self._bot.me()

            chat_members = 0
            with suppress(TelegramForbiddenError, TelegramMigrateToChat):
                chat_members = await self._bot.get_chat_member_count(chat_id=self._chat_id)

            chat_details = None
            with suppress(TelegramForbiddenError, TelegramMigrateToChat):
                chat_details = await self._bot.get_chat(chat_id=self._chat_id)

            chat_options = None
            with suppress(TelegramForbiddenError, TelegramMigrateToChat):
                chat_options = await self._bot.get_chat_member(
                    chat_id=self._chat_id,
                    user_id=self_details.id)

            user_options = None
            with suppress(TelegramForbiddenError, TelegramMigrateToChat):
                user_options = await self._bot.get_chat_member(
                    chat_id=self._chat_id,
                    user_id=self._user_id)

            self._details = RequestDetails(
                    self_details, chat_members, chat_details, chat_options, user_options)

        return self._details

    @property
    @abstractmethod
    def _payload(self) -> Payload:
        ...

    async def __call__(self) -> Request[Payload]:
        return Request(
            metadata=self._metadata,
            details=await self.details(),
            payload=self._payload,
            as_event=self._event,
        )
