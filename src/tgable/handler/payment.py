
from collections.abc import Callable

from dataclasses import dataclass

from typing import override
from typing import Protocol

from tgable.payload import PaymentPayload
from tgable.context import Context

from . import Filters
from . import Wrapper
from . import Handlers


# pylint: disable=too-few-public-methods
class PaymentHandler[ServiceT](Protocol):
    async def __call__(self, context: Context[PaymentPayload, ServiceT], /) -> None:
        ...


@dataclass(frozen=True)
class PaymentWrapper[ServiceT](Wrapper[PaymentPayload, ServiceT]):
    handler: PaymentHandler[ServiceT]

    @override
    async def __call__(self, context: Context[PaymentPayload, ServiceT]) -> None:
        await self.handler(context)


class PaymentHandlers[ServiceT](Handlers[None, PaymentPayload, ServiceT]):
    def __call__(
        self,
        /,
        filters: Filters[PaymentPayload, ServiceT] = (),
    ) -> Callable[[PaymentHandler[ServiceT]], PaymentHandler[ServiceT]]:
        # BUG: mypy#20593
        def _wrapper(handler: PaymentHandler[ServiceT]) -> PaymentWrapper[ServiceT]:
            return PaymentWrapper(filters, handler)
        return self.decorate(None, _wrapper)

    @override
    def _keyfunc(self, context: Context[PaymentPayload, ServiceT]) -> None:
        return None
