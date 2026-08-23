
from abc import ABC, abstractmethod

from collections.abc import Awaitable
from collections.abc import Iterable
from collections.abc import Callable

from dataclasses import dataclass

from tgable.payload import Payload
from tgable.context import Context


type Handler[PayloadT: Payload, ServiceT] = \
        Callable[[Context[PayloadT, ServiceT]], Awaitable[None]]

type Filters[PayloadT: Payload, ServiceT] = \
        Iterable[Callable[[Context[PayloadT, ServiceT]], bool | Awaitable[bool]]]


# BUG: mypy#18842
# type Decorate[_HandlerT] = Callable[[_HandlerT], _HandlerT]


@dataclass(frozen=True)
class Wrapper[PayloadT: Payload, ServiceT](ABC):
    filters: Filters[PayloadT, ServiceT]

    @abstractmethod
    async def __call__(self, context: Context[PayloadT, ServiceT]) -> None:
        ...


class Handlers[KeyT, PayloadT: Payload, ServiceT](ABC):
    def __init__(
        self,
        handlers: dict[KeyT, Wrapper[PayloadT, ServiceT]] | None = None,
        filters: Filters[PayloadT, ServiceT] | None = None,
    ) -> None:

        if handlers is None:
            handlers = {}
        self._handlers: dict[KeyT, Wrapper[PayloadT, ServiceT]] = handlers

        if filters is None:
            filters = []
        self._filters: Filters[PayloadT, ServiceT] = filters

    @property
    def handlers(self) -> dict[KeyT, Wrapper[PayloadT, ServiceT]]:
        return self._handlers

    def decorate[HandlerT](
        self,
        key: KeyT,
        wrapper: Callable[[HandlerT], Wrapper[PayloadT, ServiceT]],
    ) -> Callable[[HandlerT], HandlerT]:
        def _wrapper(handler: HandlerT) -> HandlerT:
            self._handlers[key] = wrapper(handler)
            return handler

        return _wrapper

    @abstractmethod
    def _keyfunc(self, context: Context[PayloadT, ServiceT]) -> KeyT:
        ...

    async def dispatch(self, context: Context[PayloadT, ServiceT]) -> None:
        handler = self._handlers.get(self._keyfunc(context))
        if handler is None:
            return

        for _filter in *self._filters, *handler.filters:
            passing = _filter(context)
            if isinstance(passing, Awaitable):
                passing = await passing
            if not passing:
                return

        await handler(context)
