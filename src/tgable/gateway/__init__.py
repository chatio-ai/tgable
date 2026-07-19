
from aiogram.exceptions import TelegramNetworkError

from aiogram.types import MenuButtonWebApp
from aiogram.types import WebAppInfo
from aiogram.types import BotCommand

from aiogram import Dispatcher
from aiogram import Bot

from tgable.factory import Factory
from tgable.dispatch import Dispatch

from .logging import log
from .logging import setup_logging
from .routing import setup_routing


# pylint: disable=too-few-public-methods
class Gateway[ServiceT]:

    def __init__(
        self,
        bot_key: str,
        factory: Factory[ServiceT],
        dispatch: Dispatch[ServiceT],
        web_app: str | None = None,
        commands: dict[str, str] | None = None,
    ) -> None:

        self._web_app = web_app
        self._commands = []
        if commands is not None:
            for name, desc in commands.items():
                self._commands.append(BotCommand(command=name, description=desc))

        self._bot = Bot(token=bot_key)
        self._dp = Dispatcher()

        setup_logging(self._dp, self._bot)
        setup_routing(self._dp, factory, dispatch)

    async def serve(self) -> None:
        async with self._bot:
            try:
                log.info("INIT bot %s", self._bot.id)
                if self._web_app is not None:
                    await self._bot.set_chat_menu_button(menu_button=MenuButtonWebApp(
                        text="...",
                        web_app=WebAppInfo(url=self._web_app),
                    ))
                await self._bot.set_my_commands(self._commands)
                log.info("POLL bot %s", self._bot.id)
                await self._dp.start_polling(self._bot)
            except TelegramNetworkError as e:
                raise SystemExit(e) from e
            finally:
                log.info("DONE bot %s", self._bot.id)
