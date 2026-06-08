
from collections.abc import Callable

from dataclasses import dataclass, field

from functools import singledispatchmethod

from tgable.payload import Payload
from tgable.payload import UnknownPayload
from tgable.payload import MessagePayload
from tgable.payload import DocumentPayload
from tgable.payload import CommandPayload
from tgable.payload import KeyboardPayload
from tgable.payload import ServicePayload
from tgable.payload import MyMemberPayload
from tgable.payload import CheckoutPayload
from tgable.payload import PaymentPayload

from tgable.context import Context

from tgable.handler import Filters
from tgable.handler import Wrapper
from tgable.handler.message import MessageHandlers
from tgable.handler.document import DocumentHandlers
from tgable.handler.command import CommandHandlers
from tgable.handler.keyboard import KeyboardHandlers
from tgable.handler.service import ServiceHandlers
from tgable.handler.mymember import MyMemberHandlers
from tgable.handler.checkout import CheckoutHandlers
from tgable.handler.payment import PaymentHandlers


# pylint: disable=too-many-instance-attributes
@dataclass(frozen=True)
class Feature[ServiceT]:
    message: MessageHandlers[ServiceT] = field(default_factory=MessageHandlers)
    document: DocumentHandlers[ServiceT] = field(default_factory=DocumentHandlers)
    command: CommandHandlers[ServiceT] = field(default_factory=CommandHandlers)
    keyboard: KeyboardHandlers[ServiceT] = field(default_factory=KeyboardHandlers)
    service: ServiceHandlers[ServiceT] = field(default_factory=ServiceHandlers)
    mymember: MyMemberHandlers[ServiceT] = field(default_factory=MyMemberHandlers)
    checkout: CheckoutHandlers[ServiceT] = field(default_factory=CheckoutHandlers)
    payment: PaymentHandlers[ServiceT] = field(default_factory=PaymentHandlers)


@dataclass(frozen=True)
class Dispatch[ServiceT](Feature[ServiceT]):
    def __init__(
        self,
        *features: Feature[ServiceT],
        filters: Filters[Payload, ServiceT] | None = None,
    ) -> None:
        def _handlers[KeyT, PayloadT: Payload, HandlersT](
            extract: Callable[[Feature[ServiceT]], dict[KeyT, Wrapper[PayloadT, ServiceT]]],
            factory: Callable[[
                dict[KeyT, Wrapper[PayloadT, ServiceT]],
                Filters[Payload, ServiceT] | None,
            ], HandlersT],
        ) -> HandlersT:
            handlers: dict[KeyT, Wrapper[PayloadT, ServiceT]] = {}
            for f in features:
                handlers.update(extract(f))
            return factory(handlers, filters)

        super().__init__(
            message=_handlers(lambda f: f.message.handlers, MessageHandlers),
            document=_handlers(lambda f: f.document.handlers, DocumentHandlers),
            command=_handlers(lambda f: f.command.handlers, CommandHandlers),
            keyboard=_handlers(lambda f: f.keyboard.handlers, KeyboardHandlers),
            service=_handlers(lambda f: f.service.handlers, ServiceHandlers),
            mymember=_handlers(lambda f: f.mymember.handlers, MyMemberHandlers),
            checkout=_handlers(lambda f: f.checkout.handlers, CheckoutHandlers),
            payment=_handlers(lambda f: f.payment.handlers, PaymentHandlers),
        )

    @singledispatchmethod
    async def dispatch(self, _payload: Payload, _context: Context[Payload, ServiceT]) -> None:
        raise NotImplementedError

    @dispatch.register
    async def _(
            self, _payload: UnknownPayload, _context: Context[UnknownPayload, ServiceT]) -> None:
        pass

    @dispatch.register
    async def _(
            self, _payload: MessagePayload, context: Context[MessagePayload, ServiceT]) -> None:
        return await self.message.dispatch(context)

    @dispatch.register
    async def _(
            self, _payload: DocumentPayload, context: Context[DocumentPayload, ServiceT]) -> None:
        return await self.document.dispatch(context)

    @dispatch.register
    async def _(
            self, _payload: CommandPayload, context: Context[CommandPayload, ServiceT]) -> None:
        return await self.command.dispatch(context)

    @dispatch.register
    async def _(
            self, _payload: KeyboardPayload, context: Context[KeyboardPayload, ServiceT]) -> None:
        if context.request.payload.command.startswith('_'):
            return await self.keyboard.dispatch(context)

        return await self.command.dispatch(context)

    @dispatch.register
    async def _(
            self, _payload: ServicePayload, context: Context[ServicePayload, ServiceT]) -> None:
        return await self.service.dispatch(context)

    @dispatch.register
    async def _(
            self, _payload: MyMemberPayload, context: Context[MyMemberPayload, ServiceT]) -> None:
        return await self.mymember.dispatch(context)

    @dispatch.register
    async def _(
            self, _payload: CheckoutPayload, context: Context[CheckoutPayload, ServiceT]) -> None:
        return await self.checkout.dispatch(context)

    @dispatch.register
    async def _(
            self, _payload: PaymentPayload, context: Context[PaymentPayload, ServiceT]) -> None:
        return await self.payment.dispatch(context)
