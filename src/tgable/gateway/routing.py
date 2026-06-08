
from collections.abc import Awaitable
from collections.abc import Callable

from aiogram.types import TelegramObject

from aiogram.types import Message
from aiogram.types import CallbackQuery
from aiogram.types import ChatMemberUpdated
from aiogram.types import PreCheckoutQuery

from aiogram.dispatcher.event.telegram import TelegramEventObserver
from aiogram.dispatcher.event.bases import NextMiddlewareType

from aiogram import Dispatcher

from tgable.request import Parsing
from tgable.request.member import MemberParsing
from tgable.request.message import MessageParsing
from tgable.request.callback import CallbackParsing
from tgable.request.checkout import CheckoutParsing

from tgable.factory import Factory
from tgable.dispatch import Dispatch

from tgable.execute import handle_event


def _wrap_handle_event[TelegramObjectT: TelegramObject, ServiceT](
    objtype: type[TelegramObjectT],
    parsing: Callable[[TelegramObjectT], Parsing[TelegramObjectT]],
    factory: Factory[ServiceT],
    dispatch: Dispatch[ServiceT],
) -> Callable[[
    NextMiddlewareType[TelegramObject],
    TelegramObject,
    dict[str, object],
], Awaitable[object]]:
    async def _wrapper(
        _handler: NextMiddlewareType[TelegramObject],
        event: TelegramObject,
        _data: dict[str, object],
    ) -> None:
        assert isinstance(event, objtype)
        await handle_event(parsing(event), factory, dispatch)
    return _wrapper


def setup_routing[ServiceT](
    dp: Dispatcher,
    factory: Factory[ServiceT],
    dispatch: Dispatch[ServiceT],
) -> None:
    def _setup_handler[TelegramObjectT: TelegramObject](
        observer: TelegramEventObserver,
        objtype: type[TelegramObjectT],
        parsing: Callable[[TelegramObjectT], Parsing[TelegramObjectT]],
    ) -> None:
        observer.outer_middleware.register(_wrap_handle_event(objtype, parsing, factory, dispatch))

    _setup_handler(dp.message, Message, MessageParsing)
    # _setup_handler(self._dp.edited_message, Message, MessageParsing)
    _setup_handler(dp.callback_query, CallbackQuery, CallbackParsing)
    _setup_handler(dp.my_chat_member, ChatMemberUpdated, MemberParsing)
    _setup_handler(dp.pre_checkout_query, PreCheckoutQuery, CheckoutParsing)
