
from dataclasses import dataclass

from typing import override

from aiogram.types import InlineKeyboardMarkup

from aiogram.enums import ParseMode

from . import Channel


@dataclass(frozen=True)
class CallbackChannel(Channel):
    _query_object_id: str

    @override
    async def message_render(
        self,
        text: str,
        parse_mode: ParseMode | None = None,
        buttons: InlineKeyboardMarkup | None = None,
        *,
        force: bool = False,
    ) -> None:
        if force:
            await self.message_answer(text=text, parse_mode=parse_mode, buttons=buttons)
            return
        await self.message_update(text=text, parse_mode=parse_mode, buttons=buttons)

    async def callback_reply(self, text: str | None = None) -> None:
        await self._control.bot.answer_callback_query(
                self._query_object_id, text=text)
