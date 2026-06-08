
import logging

from enum import Enum, auto

from collections.abc import AsyncIterator

from dataclasses import dataclass

from typing import Self

from aiogram.exceptions import TelegramBadRequest

from aiogram.types import InlineKeyboardMarkup
from aiogram.types import ReplyKeyboardMarkup
from aiogram.types import ReplyKeyboardRemove
from aiogram.types import LabeledPrice

from aiogram.enums import ChatAction
from aiogram.enums import ParseMode

from tgable.content import iter_content

from tgable.metadata import Control

from tgable.limiter import Limiter


log = logging.getLogger(__name__)


type KeyboardMarkup = InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove


class ChannelAddress(Enum):
    CURRENT = auto()
    GENERAL = auto()
    PRIVATE = auto()


@dataclass(frozen=True)
class Channel:
    _limiter: Limiter
    _control: Control

    def _channel_address(self, address: ChannelAddress | None) -> tuple[int, int | None]:
        if address is None:
            address = ChannelAddress.CURRENT

        match address:
            case ChannelAddress.CURRENT:
                return self._control.chat_id, self._control.thread_id
            case ChannelAddress.GENERAL:
                return self._control.chat_id, 0
            case ChannelAddress.PRIVATE:
                return self._control.user_id, 0

    # pylint: disable=too-many-arguments
    async def _message_answer(
        self,
        text: str,
        *,
        reply_to: int | bool | None = None,
        parse_mode: ParseMode | None = None,
        buttons: KeyboardMarkup | None = None,
        address: ChannelAddress | None = None,
    ) -> None:
        if parse_mode is None:
            parse_mode = ParseMode.MARKDOWN_V2

        if reply_to is True:
            reply_to = self._control.flow.last_message_id

        chat_id, thread_id = self._channel_address(address)

        if not await self._limiter.wait_msg():
            return

        message_id = None
        try:
            message = (await self._control.bot.send_message(
                chat_id=chat_id,
                message_thread_id=thread_id,
                reply_to_message_id=reply_to,
                text=text,
                parse_mode=parse_mode,
                reply_markup=buttons))
            self._control.flow.menu_message_id = message_id = message.message_id
        finally:
            log.info("<< message=%s length=%s", message_id, len(text))
            log.debug("%s\n", text)

    async def message_reply(
        self,
        text: str,
        *,
        parse_mode: ParseMode | None = None,
        buttons: KeyboardMarkup | None = None,
    ) -> None:
        await self._message_answer(text, parse_mode=parse_mode, buttons=buttons, reply_to=True)

    async def message_answer(
        self,
        text: str,
        *,
        parse_mode: ParseMode | None = None,
        buttons: KeyboardMarkup | None = None,
    ) -> None:
        await self._message_answer(text, parse_mode=parse_mode, buttons=buttons, reply_to=False)

    async def message_answer_general(
        self,
        text: str,
        *,
        parse_mode: ParseMode | None = None,
        buttons: KeyboardMarkup | None = None,
    ) -> None:
        await self._message_answer(
                text, parse_mode=parse_mode, buttons=buttons, address=ChannelAddress.GENERAL)

    async def message_answer_private(
        self,
        text: str,
        *,
        parse_mode: ParseMode | None = None,
        buttons: KeyboardMarkup | None = None,
    ) -> None:
        await self._message_answer(
                text, parse_mode=parse_mode, buttons=buttons, address=ChannelAddress.PRIVATE)

    async def message_stream(
        self,
        stream: AsyncIterator[str],
        parse_mode: ParseMode | None = None,
        buttons: InlineKeyboardMarkup | None = None,
    ) -> None:
        reply_to = self._control.flow.last_message_id

        ready = None
        async for chunk in iter_content(_SendTyping(self, stream)):
            if ready is not None:
                await self._message_answer(
                        text=ready, parse_mode=parse_mode, reply_to=reply_to)
                reply_to = None
            ready = chunk

        if ready is None:
            ready = ""

        await self._message_answer(
                text=ready, parse_mode=parse_mode, reply_to=reply_to, buttons=buttons)

    async def message_delete(self) -> None:
        if self._control.flow.menu_message_id is None:
            return

        if not await self._limiter.wait_api():
            return

        await self._control.bot.delete_message(
            chat_id=self._control.chat_id,
            message_id=self._control.flow.menu_message_id)

    async def message_update(
        self,
        text: str,
        parse_mode: ParseMode | None = None,
        buttons: InlineKeyboardMarkup | None = None,
    ) -> None:
        if self._control.flow.menu_message_id is None:
            return

        if parse_mode is None:
            parse_mode = ParseMode.MARKDOWN_V2

        if not await self._limiter.wait_msg():
            return

        message_id = None
        try:
            message = await self._control.bot.edit_message_text(
                chat_id=self._control.chat_id,
                text=text,
                parse_mode=parse_mode,
                message_id=self._control.flow.menu_message_id,
                reply_markup=buttons)
            assert not isinstance(message, bool)
            self._control.flow.menu_message_id = message_id = message.message_id
        except TelegramBadRequest as err:
            err_msg = err.message.removeprefix('Bad Request: ')
            if not err_msg.startswith('message is not modified: '):
                raise
        finally:
            log.info("<< message=%s length=%s", message_id, len(text))
            log.debug("%s\n", text)

    async def message_render(
        self,
        text: str,
        parse_mode: ParseMode | None = None,
        buttons: InlineKeyboardMarkup | None = None,
        *,
        force: bool = False,
    ) -> None:
        _ = force
        await self.message_answer(text=text, parse_mode=parse_mode, buttons=buttons)

    async def message_markup(
        self,
        buttons: InlineKeyboardMarkup | None = None,
    ) -> None:
        if self._control.flow.menu_message_id is None:
            return

        if not await self._limiter.wait_msg():
            return

        try:
            await self._control.bot.edit_message_reply_markup(
                chat_id=self._control.chat_id,
                message_id=self._control.flow.menu_message_id,
                reply_markup=buttons)
        except TelegramBadRequest as err:
            err_msg = err.message.removeprefix('Bad Request: ')
            if not err_msg.startswith('message is not modified: '):
                raise

    async def typing_notify(self) -> None:
        if not await self._limiter.test():
            return

        await self._control.bot.send_chat_action(
            chat_id=self._control.chat_id,
            message_thread_id=self._control.thread_id,
            action=ChatAction.TYPING)

    async def create_invoice(
            self, value: int, title: str, description: str, label: str) -> str:
        return await self._control.bot.create_invoice_link(
            title=title,
            description=description,
            payload=title,
            currency="XTR",
            prices=[
                LabeledPrice(
                    label=label,
                    amount=value,
                ),
            ],
        )

    async def topic_create(self, title: str) -> None:
        await self._control.bot.create_forum_topic(
            chat_id=self._control.chat_id,
            name=title,
        )


class _SendTyping:
    def __init__(self, channel: Channel, content: AsyncIterator[str]) -> None:
        self._channel = channel
        self._content = content

    def __aiter__(self) -> Self:
        return self

    async def __anext__(self) -> str:
        await self._channel.typing_notify()
        return await anext(self._content)
