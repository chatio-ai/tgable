
import logging

from collections.abc import Iterable, Iterator, AsyncIterator

from typing import Self


from mistletoe import token as base_token
from mistletoe import span_token


from aiogram.utils.text_decorations import MarkdownDecoration


log = logging.getLogger(__name__)


_markdown = MarkdownDecoration()


def escape_text(text: str) -> str:
    return _markdown.unparse(text, [])


def _commonmark_to_telegramv2_once(token: base_token.Token) -> Iterator[str]:
    embedded = "".join(_commonmark_to_telegramv2_iter(token.children))

    match token:
        case span_token.Emphasis():
            yield _markdown.italic(embedded)
        case span_token.Strong():
            yield _markdown.bold(embedded)
        case span_token.Strikethrough():
            yield _markdown.strikethrough(embedded)
        case span_token.InlineCode():
            yield _markdown.code(embedded)
        case span_token.EscapeSequence():
            yield embedded
        case span_token.RawText():
            yield escape_text(token.content)
        case span_token.LineBreak():
            yield "\n"
        case span_token.Link():
            yield _markdown.link(embedded, escape_text(token.target))
        case span_token.Image():
            yield _markdown.link(embedded, escape_text(token.src))
        case _:
            raise RuntimeError(token)


def _commonmark_to_telegramv2_iter(tokens: Iterable[base_token.Token] | None) -> Iterator[str]:
    if tokens is None:
        return

    for token in tokens:
        yield from _commonmark_to_telegramv2_once(token)


def _commonmark_to_telegramv2(text: str) -> str:
    embedded = "".join(_commonmark_to_telegramv2_iter(span_token.tokenize_inner(text)))

    if text.startswith("#"):
        return _markdown.underline(embedded.removesuffix("#")) + "\n"

    return embedded


class EscapeChars:
    def __init__(self, content: AsyncIterator[str]) -> None:
        self.content = content
        self.cfblock = False

    def __aiter__(self) -> Self:
        return self

    async def __anext__(self) -> str:
        line = await anext(self.content)

        if line.lstrip().startswith("```"):
            self.cfblock = not self.cfblock
            return line

        if self.cfblock:
            return escape_text(line)

        return _commonmark_to_telegramv2(line)
