
from collections.abc import AsyncIterator
from typing import Self

import logging


log = logging.getLogger(__name__)


class ChunkToLine:
    def __init__(self, content: AsyncIterator[str]) -> None:
        self.content = content
        self.empty = False
        self.line = ""
        self.chunks: list[str] = []

    def __aiter__(self) -> Self:
        return self

    async def __anext__(self) -> str:
        if self.empty:
            raise StopAsyncIteration

        while not self.line.endswith("\n"):
            if not self.chunks:
                try:
                    buffer = await anext(self.content)
                except StopAsyncIteration:
                    self.empty = True
                    buffer = ""
                self.chunks = buffer.splitlines(keepends=True)

            if not self.chunks:
                break

            self.line += self.chunks.pop(0)

        tmp_line = self.line
        self.line = ""

        return tmp_line


class LineToBlock:
    def __init__(self, content: AsyncIterator[str], limit: int) -> None:
        self.content = content
        self.limit = limit
        self.empty = False
        self.block = ""
        self.last_ln = ""

        self.open_cb = ""
        self.close_cb = ""

    def __aiter__(self) -> Self:
        return self

    def _log_line(self) -> None:
        if self.last_ln:
            log.debug(
                ": %4s/%4s %4s/%4s %s\t", len(self.last_ln), len(self.block),
                len(self.last_ln.encode()), len(self.block.encode()),
                self.last_ln.removesuffix('\n'))

    async def __anext__(self) -> str:
        if self.empty:
            raise StopAsyncIteration

        while len(self.block + self.last_ln + self.close_cb) < self.limit:
            self.block += self.last_ln
            self._log_line()

            try:
                self.last_ln = await anext(self.content)
            except StopAsyncIteration:
                self.empty = True
                break

            if self.last_ln.lstrip().startswith("```"):
                if self.open_cb or self.close_cb:
                    self.open_cb = ""
                    self.close_cb = ""
                else:
                    self.open_cb = self.last_ln
                    self.close_cb = "".join(c for c in self.last_ln if c.isspace() or c == '`')

        tmp_block = self.block + self.close_cb

        self.block = self.open_cb + self.last_ln
        self.last_ln = ""

        self._log_line()

        return tmp_block
