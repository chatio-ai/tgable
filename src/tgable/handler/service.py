
from collections.abc import Callable

from dataclasses import dataclass

from typing import override
from typing import Protocol

from tgable.payload import ServicePayloadType
from tgable.payload import ServicePayload
from tgable.context import Service
from tgable.context import Context

from . import Filters
from . import Wrapper
from . import Handlers


# pylint: disable=too-few-public-methods
class ServiceHandler[ServiceT: Service](Protocol):
    async def __call__(
            self, context: Context[ServicePayload, ServiceT], caption: str | None, /) -> None:
        ...


@dataclass(frozen=True)
class ServiceWrapper[ServiceT: Service](Wrapper[ServicePayload, ServiceT]):
    handler: ServiceHandler[ServiceT]

    async def __call__(self, context: Context[ServicePayload, ServiceT]) -> None:
        await self.handler(context, context.request.payload.caption)


class ServiceHandlers[ServiceT: Service](Handlers[ServicePayloadType, ServicePayload, ServiceT]):
    def __call__(
        self,
        service: ServicePayloadType,
        /,
        filters: Filters[ServicePayload, ServiceT] = (),
    ) -> Callable[[ServiceHandler[ServiceT]], ServiceHandler[ServiceT]]:
        # BUG: mypy#20593
        def _wrapper(handler: ServiceHandler[ServiceT]) -> ServiceWrapper[ServiceT]:
            return ServiceWrapper(filters, handler)
        return self.decorate(service, _wrapper)

    @override
    def _keyfunc(self, context: Context[ServicePayload, ServiceT]) -> ServicePayloadType:
        return context.request.payload.service
