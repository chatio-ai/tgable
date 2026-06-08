
import logging

from contextlib import suppress

from aiogram.exceptions import TelegramForbiddenError
from aiogram.exceptions import TelegramMigrateToChat

from aiogram.types import TelegramObject

from tgable.metadata import binding_var

from tgable.request import Parsing

from tgable.channel.callback import CallbackChannel

from tgable.payload import MessagePayload
from tgable.payload import CommandPayload
from tgable.context import Context
from tgable.factory import Factory
from tgable.dispatch import Dispatch

from tgable.content import reports


log = logging.getLogger(__name__)


async def handle_event[ServiceT](
    parsing: Parsing[TelegramObject],
    factory: Factory[ServiceT],
    dispatch: Dispatch[ServiceT],
) -> None:

    channel = None

    try:
        binding_var.set(parsing.binding)

        channel = parsing.channel(factory.limiter(parsing.binding))

        request = await parsing()

        log.info(">> %s/%s %s", parsing.as_text, request.payload.as_type, request.payload)
        if isinstance(request.payload, (MessagePayload, CommandPayload)) \
                and request.payload.content is not None:
            log.debug("%s", request.payload.content)

        context = Context(
            request=request,
            channel=channel,
            service=factory.service(parsing.binding),
        )
        locking = factory.locking(parsing.binding)

        if isinstance(context.channel, CallbackChannel):
            if locking.locked():
                await context.channel.callback_reply("Flood control is in effect! Please wait.")
                return
            await context.channel.callback_reply()

        async with locking:
            await dispatch.dispatch(request.payload, context)

    except Exception as exc:    # pylint: disable=broad-exception-caught
        log.exception("", exc_info=exc)
        if channel is not None:
            with suppress(TelegramForbiddenError, TelegramMigrateToChat):
                await channel.message_reply(reports.exc(exc))
