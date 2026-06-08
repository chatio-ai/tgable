
from collections.abc import Callable

from dataclasses import dataclass

from typing import override
from typing import Protocol

from tgable.payload import MessagePayload
from tgable.context import Service
from tgable.context import Context

from . import Filters
from . import Wrapper
from . import Handlers


# pylint: disable=too-few-public-methods
class MessageHandler[ServiceT: Service](Protocol):
    async def __call__(self, context: Context[MessagePayload, ServiceT], content: str, /) -> None:
        ...


@dataclass(frozen=True)
class MessageWrapper[ServiceT: Service](Wrapper[MessagePayload, ServiceT]):
    handler: MessageHandler[ServiceT]

    @override
    async def __call__(self, context: Context[MessagePayload, ServiceT]) -> None:
        await self.handler(context, context.request.payload.content)


class MessageHandlers[ServiceT: Service](Handlers[None, MessagePayload, ServiceT]):
    def __call__(
        self,
        /,
        filters: Filters[MessagePayload, ServiceT] = (),
    ) -> Callable[[MessageHandler[ServiceT]], MessageHandler[ServiceT]]:
        # BUG: mypy#20593
        def _wrapper(handler: MessageHandler[ServiceT]) -> MessageWrapper[ServiceT]:
            return MessageWrapper(filters, handler)
        return self.decorate(None, _wrapper)

    @override
    def _keyfunc(self, context: Context[MessagePayload, ServiceT]) -> None:
        return None
