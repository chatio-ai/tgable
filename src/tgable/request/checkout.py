
from typing import override

from aiogram.types import PreCheckoutQuery
from aiogram.types import User

from tgable.metadata import Objects

from tgable.payload import CheckoutPayload
from tgable.limiter import Limiter
from tgable.channel.checkout import CheckoutChannel

from . import Parsing


class CheckoutParsing(Parsing[PreCheckoutQuery]):

    @property
    @override
    def _object_id(self) -> str:
        return self._event.id

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
    def _chat(self) -> None:
        return None

    @property
    @override
    def _thread_id(self) -> None:
        return None

    @override
    def channel(self, limiter: Limiter) -> CheckoutChannel:
        return CheckoutChannel(limiter, self._control, self._event.id)

    @property
    @override
    def _payload(self) -> CheckoutPayload:
        return CheckoutPayload(
            amount=self._event.total_amount,
            invoice=self._event.invoice_payload,
        )
