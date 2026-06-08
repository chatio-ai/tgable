
from collections.abc import Callable

from dataclasses import dataclass

from typing import override
from typing import Protocol

from tgable.payload import MyMemberPayloadType
from tgable.payload import MyMemberPayload
from tgable.context import Service
from tgable.context import Context

from . import Filters
from . import Wrapper
from . import Handlers


# pylint: disable=too-few-public-methods
class MyMemberHandler[ServiceT: Service](Protocol):
    async def __call__(
            self, context: Context[MyMemberPayload, ServiceT], caption: str | None, /) -> None:
        ...


@dataclass(frozen=True)
class MyMemberWrapper[ServiceT: Service](Wrapper[MyMemberPayload, ServiceT]):
    handler: MyMemberHandler[ServiceT]

    async def __call__(self, context: Context[MyMemberPayload, ServiceT]) -> None:
        await self.handler(context, context.request.payload.caption)


class MyMemberHandlers[ServiceT: Service](
        Handlers[MyMemberPayloadType, MyMemberPayload, ServiceT]):
    def __call__(
        self,
        mymember: MyMemberPayloadType,
        /,
        filters: Filters[MyMemberPayload, ServiceT] = (),
    ) -> Callable[[MyMemberHandler[ServiceT]], MyMemberHandler[ServiceT]]:
        # BUG: mypy#20593
        def _wrapper(handler: MyMemberHandler[ServiceT]) -> MyMemberWrapper[ServiceT]:
            return MyMemberWrapper(filters, handler)
        return self.decorate(mymember, _wrapper)

    @override
    def _keyfunc(self, context: Context[MyMemberPayload, ServiceT]) -> MyMemberPayloadType:
        return context.request.payload.mymember
