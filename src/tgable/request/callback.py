
from typing import override

from aiogram.types import CallbackQuery
from aiogram.types import Message
from aiogram.types import User
from aiogram.types import Chat

from tgable.metadata import Objects

from tgable.payload import KeyboardPayload
from tgable.limiter import Limiter
from tgable.channel.callback import CallbackChannel

from . import Parsing


class CallbackParsing(Parsing[CallbackQuery]):

    @property
    @override
    def _object_id(self) -> str:
        return self._event.id

    @property
    @override
    def _flow(self) -> Objects:
        assert isinstance(self._event.message, Message)
        return Objects(
            last_message_id=self._event.message.message_id,
            menu_message_id=self._event.message.message_id,
        )

    @property
    @override
    def _user(self) -> User:
        return self._event.from_user

    @property
    @override
    def _chat(self) -> Chat:
        assert isinstance(self._event.message, Message)
        return self._event.message.chat

    @property
    @override
    def _thread_id(self) -> int | None:
        assert isinstance(self._event.message, Message)
        return self._event.message.message_thread_id

    @override
    def channel(self, limiter: Limiter) -> CallbackChannel:
        return CallbackChannel(limiter, self._control, self._event.id)

    @property
    @override
    def _payload(self) -> KeyboardPayload:
        if self._event.data is None:
            raise RuntimeError

        if self._event.data.startswith('/'):
            return KeyboardPayload(self._event.data)

        version, _, keyboard = self._event.data.partition(':')
        keyboard, _, cmdline = keyboard.partition(':')
        return KeyboardPayload(cmdline, keyboard, version)
