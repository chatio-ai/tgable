
from dataclasses import dataclass

from . import Channel


@dataclass(frozen=True)
class CheckoutChannel(Channel):
    _pre_checkout_id: str

    async def checkout(self, *, confirm: bool | None = None) -> None:
        if confirm is None:
            raise ValueError

        await self._control.bot.answer_pre_checkout_query(
            pre_checkout_query_id=self._pre_checkout_id, ok=confirm)
