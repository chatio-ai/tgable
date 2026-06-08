
from typing import override

from aiogram.types import ChatMemberUpdated
from aiogram.types import User
from aiogram.types import Chat

from tgable.metadata import Objects

from tgable.payload import MyMemberPayload
from tgable.payload import MyMemberPayloadType

from . import Parsing


class MemberParsing(Parsing[ChatMemberUpdated]):

    @property
    @override
    def _object_id(self) -> str:
        return ""

    @property
    @override
    def _flow(self) -> Objects:
        return Objects()

    @property
    @override
    def _user(self) -> User:
        return self._event.from_user

    @property
    @override
    def _chat(self) -> Chat:
        return self._event.chat

    @property
    @override
    def _thread_id(self) -> None:
        return None

    @property
    @override
    def _payload(self) -> MyMemberPayload:
        old_status = self._event.old_chat_member.status
        new_status = self._event.new_chat_member.status

        if old_status in ['left', 'kicked'] and new_status not in ['left', 'kicked']:
            return MyMemberPayload(
                MyMemberPayloadType.INVITED, old_status, new_status, self._event.chat.title)

        return MyMemberPayload(
                MyMemberPayloadType.UNKNOWN, old_status, new_status, self._event.chat.title)
