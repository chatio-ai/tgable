
import logging
import pathlib

from typing import override

from tgable.metadata import binding_var
from tgable.metadata import Binding


class ContextFormatter(logging.Formatter):

    @override
    def formatMessage(self, record: logging.LogRecord) -> str:
        binding = binding_var.get()
        if binding is not None:
            prefix = f"bot={binding.bot_id} "
            prefix += f"chat={binding.chat_id}:{binding.thread_id} "
            prefix += f"user={binding.user_id}"
            record.message = f"{prefix} {record.message}"
        return super().formatMessage(record)


class ContextFileHandler(logging.Handler):

    def __init__(self, name: str, path: pathlib.Path) -> None:
        super().__init__()

        self._name = name
        self._path = path
        self._handlers: \
            dict[tuple[Binding.BotId, Binding.ChatId, Binding.ThreadId], logging.Handler] = {}

    def _handler(self, binding: Binding) -> logging.Handler:
        handler = self._handlers.get((binding.bot_id, binding.chat_id, binding.thread_id))

        if handler is None:
            dirpath = self._path.joinpath(
                    f"./{binding.bot_id}/{binding.chat_id}/{binding.thread_id}/")
            dirpath.mkdir(parents=True, exist_ok=True)

            handler = logging.FileHandler(dirpath.joinpath(f"{self._name}.log"))

            handler.setFormatter(self.formatter)
            handler.setLevel(self.level)

            self._handlers[(binding.bot_id, binding.chat_id, binding.thread_id)] = handler

        return handler

    @override
    def emit(self, record: logging.LogRecord) -> None:
        binding = binding_var.get()
        if binding is not None:
            self._handler(binding).emit(record)
