
from collections.abc import Callable

from dataclasses import dataclass

from typing import override
from typing import Protocol

from tgable.payload import CheckoutPayload
from tgable.context import Context

from . import Filters
from . import Wrapper
from . import Handlers


# pylint: disable=too-few-public-methods
class CheckoutHandler[ServiceT](Protocol):
    async def __call__(self, context: Context[CheckoutPayload, ServiceT], /) -> None:
        ...


@dataclass(frozen=True)
class CheckoutWrapper[ServiceT](Wrapper[CheckoutPayload, ServiceT]):
    handler: CheckoutHandler[ServiceT]

    @override
    async def __call__(self, context: Context[CheckoutPayload, ServiceT]) -> None:
        await self.handler(context)


class CheckoutHandlers[ServiceT](Handlers[None, CheckoutPayload, ServiceT]):
    def __call__(
        self,
        /,
        filters: Filters[CheckoutPayload, ServiceT] = (),
    ) -> Callable[[CheckoutHandler[ServiceT]], CheckoutHandler[ServiceT]]:
        # BUG: mypy#20593
        def _wrapper(handler: CheckoutHandler[ServiceT]) -> CheckoutWrapper[ServiceT]:
            return CheckoutWrapper(filters, handler)
        return self.decorate(None, _wrapper)

    @override
    def _keyfunc(self, context: Context[CheckoutPayload, ServiceT]) -> None:
        return None
