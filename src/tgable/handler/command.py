
from collections.abc import Callable

from dataclasses import dataclass

from typing import override
from typing import Protocol
from typing import Any

from tgable.payload import CommandPayload
from tgable.context import Context

from . import Filters
from . import Wrapper
from . import Handlers


# pylint: disable=too-few-public-methods
class CommandHandler[ServiceT](Protocol):
    async def __call__(
            self, context: Context[CommandPayload, ServiceT], /,
            *args: Any, **kwargs: Any) -> None:
        ...


@dataclass(frozen=True)
class CommandWrapper[ServiceT](Wrapper[CommandPayload, ServiceT]):
    handler: CommandHandler[ServiceT]

    async def __call__(self, context: Context[CommandPayload, ServiceT]) -> None:
        await self.handler(context, *context.request.payload.options)


class CommandHandlers[ServiceT](Handlers[str, CommandPayload, ServiceT]):
    def __call__(
        self,
        command: str,
        /,
        filters: Filters[CommandPayload, ServiceT] = (),
    ) -> Callable[[CommandHandler[ServiceT]], CommandHandler[ServiceT]]:
        # BUG: mypy#20593
        def _wrapper(handler: CommandHandler[ServiceT]) -> CommandWrapper[ServiceT]:
            return CommandWrapper(filters, handler)
        return self.decorate(command, _wrapper)

    @override
    def _keyfunc(self, context: Context[CommandPayload, ServiceT]) -> str:
        return context.request.payload.command
