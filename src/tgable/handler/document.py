
from collections.abc import Callable

from dataclasses import dataclass

from typing import override
from typing import Protocol

from tgable.payload import DocumentPayload
from tgable.context import Service
from tgable.context import Context

from . import Filters
from . import Wrapper
from . import Handlers


# pylint: disable=too-few-public-methods
class DocumentHandler[ServiceT: Service](Protocol):
    async def __call__(
            self, context: Context[DocumentPayload, ServiceT], content: str | None, /) -> None:
        ...


@dataclass(frozen=True)
class DocumentWrapper[ServiceT: Service](Wrapper[DocumentPayload, ServiceT]):
    handler: DocumentHandler[ServiceT]

    @override
    async def __call__(self, context: Context[DocumentPayload, ServiceT]) -> None:
        await self.handler(context, context.request.payload.content)


class DocumentHandlers[ServiceT: Service](Handlers[None, DocumentPayload, ServiceT]):
    def __call__(
        self,
        /,
        filters: Filters[DocumentPayload, ServiceT] = (),
    ) -> Callable[[DocumentHandler[ServiceT]], DocumentHandler[ServiceT]]:
        # BUG: mypy#20593
        def _wrapper(handler: DocumentHandler[ServiceT]) -> DocumentWrapper[ServiceT]:
            return DocumentWrapper(filters, handler)
        return self.decorate(None, _wrapper)

    @override
    def _keyfunc(self, context: Context[DocumentPayload, ServiceT]) -> None:
        return None
