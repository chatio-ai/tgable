
from collections.abc import AsyncIterator
from collections.abc import Callable

from .transforms import ChunkToLine
from .telegramv2 import EscapeChars
from .transforms import LineToBlock


MAX_TEXT_LENGTH = 4096


def iter_content(content: AsyncIterator[str]) -> AsyncIterator[str]:

    conversions: list[Callable[[AsyncIterator[str]], AsyncIterator[str]]] = [
        ChunkToLine,
        EscapeChars,
        lambda content: LineToBlock(content, MAX_TEXT_LENGTH),
    ]

    for convert in conversions:
        content = convert(content)

    return content
