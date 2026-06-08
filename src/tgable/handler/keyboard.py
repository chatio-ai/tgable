
from collections.abc import Callable

from dataclasses import dataclass

from typing import override
from typing import Protocol
from typing import Any

from aiogram.types import InlineKeyboardMarkup

from tgable.payload import KeyboardPayload
from tgable.context import Service
from tgable.context import Context

from . import Filters
from . import Wrapper
from . import Handlers


# pylint: disable=too-few-public-methods
class KeyboardHandler[ServiceT: Service](Protocol):
    def __call__(
            self, context: Context[KeyboardPayload, ServiceT], /,
            *args: Any, **kwargs: Any) -> InlineKeyboardMarkup:
        ...


@dataclass(frozen=True)
class KeyboardWrapper[ServiceT: Service](Wrapper[KeyboardPayload, ServiceT]):
    handler: KeyboardHandler[ServiceT]

    async def __call__(self, context: Context[KeyboardPayload, ServiceT]) -> None:
        await context.channel.message_markup(
                buttons=self.handler(context, *context.request.payload.options))


class KeyboardHandlers[ServiceT: Service](Handlers[str, KeyboardPayload, ServiceT]):
    def __call__(
        self,
        keyboard: str,
        /,
        filters: Filters[KeyboardPayload, ServiceT] = (),
    ) -> Callable[[KeyboardHandler[ServiceT]], KeyboardHandler[ServiceT]]:
        # BUG: mypy#20593
        def _wrapper(handler: KeyboardHandler[ServiceT]) -> KeyboardWrapper[ServiceT]:
            return KeyboardWrapper(filters, handler)
        return self.decorate(keyboard, _wrapper)

    @override
    def _keyfunc(self, context: Context[KeyboardPayload, ServiceT]) -> str:
        return context.request.payload.command
