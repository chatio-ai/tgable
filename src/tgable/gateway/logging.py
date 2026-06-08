
import json
import logging

from typing import Any

from aiogram.types import TelegramObject
from aiogram import Dispatcher
from aiogram import Bot

from aiogram.client.session.middlewares.base import NextRequestMiddlewareType

from aiogram.dispatcher.event.bases import NextMiddlewareType

from aiogram.methods.base import TelegramType
from aiogram.methods import Response
from aiogram.methods import TelegramMethod

from aiogram.methods import GetUpdates


log = logging.getLogger(__package__)


_no_log_methods: tuple[type[TelegramMethod[Any]], ...] = (
    GetUpdates,
)


async def _log_bot_update_event(
    handler: NextMiddlewareType[TelegramObject],
    event: TelegramObject,
    data: dict[str, object],
) -> object:
    _event = event.model_dump(exclude_none=True, exclude_defaults=True)
    log.debug(
        "$ %s %s", type(event).__name__, json.dumps(_event, indent=2, ensure_ascii=False))

    return await handler(event, data)


async def _log_bot_make_request(
    make_request: NextRequestMiddlewareType[TelegramType],
    bot: Bot,
    method: TelegramMethod[TelegramType],
) -> Response[TelegramType]:
    if type(method) not in _no_log_methods:
        _method = bot.session.prepare_value(
            method.model_dump(exclude_none=True, exclude_defaults=True),
            bot=bot, files={}, _dumps_json=False)
        log.debug(
            "< %s %s", type(method).__name__, json.dumps(_method, indent=2, ensure_ascii=False))

    result = await make_request(bot, method)

    if type(method) not in _no_log_methods:
        _result = bot.session.prepare_value(
            result.model_dump(exclude_none=True, exclude_defaults=True)
            if isinstance(result, TelegramObject) else result,
            bot=bot, files={}, _dumps_json=False)
        log.debug(
            "> %s %s", type(result).__name__, json.dumps(_result, indent=2, ensure_ascii=False))

    return result


def setup_logging(dp: Dispatcher, bot: Bot) -> None:
    dp.update.middleware.register(_log_bot_update_event)
    bot.session.middleware.register(_log_bot_make_request)
