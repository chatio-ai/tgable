
from datetime import datetime
from typing import override

from aiogram.utils.text_decorations import TextDecoration
from aiogram.enums import MessageEntityType
from aiogram.types import MessageEntity


class _CommonmarkDecoration(TextDecoration):

    @override
    def apply_entity(self, entity: MessageEntity, text: str) -> str:
        if entity.type == MessageEntityType.MENTION and text.endswith("bot"):
            return ""
        return super().apply_entity(entity, text)

    @override
    def link(self, value: str, link: str) -> str:
        return f'[{value}]({link})'

    @override
    def bold(self, value: str) -> str:
        return f'**{value}**'

    @override
    def italic(self, value: str) -> str:
        return f'_{value}_'

    @override
    def underline(self, value: str) -> str:
        return f'__{value}__'

    @override
    def strikethrough(self, value: str) -> str:
        return f'~~{value}~~'

    @override
    def spoiler(self, value: str) -> str:
        return f'||{value}||'

    @override
    def code(self, value: str) -> str:
        return f'`{value}`'

    @override
    def pre(self, value: str) -> str:
        return f'```\n{value}\n```'

    @override
    def pre_language(self, value: str, language: str) -> str:
        return f'```{language}\n{value}\n```'

    @override
    def quote(self, value: str) -> str:
        return value

    @override
    def custom_emoji(self, value: str, custom_emoji_id: str) -> str:
        raise NotImplementedError

    @override
    def blockquote(self, value: str) -> str:
        return "\n".join(f'> {line}' for line in value.splitlines())

    @override
    def expandable_blockquote(self, value: str) -> str:
        return "\n".join(f'> {line}' for line in value.splitlines())

    @override
    def date_time(
        self,
        value: str,
        unix_time: int | datetime,
        date_time_format: str | None = None,
    ) -> str:
        raise NotImplementedError


_commonmark = _CommonmarkDecoration()


def reconstruct(text: str, entities: list[MessageEntity]) -> str:
    return _commonmark.unparse(text, entities)
