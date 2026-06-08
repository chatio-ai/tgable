
import asyncio

from collections.abc import AsyncIterator

import pytest

from tgable.content.telegramv2 import EscapeChars


COMMONMARK_TO_TELEGRAMV2_TESTS = [
    ("", ""),

    ("test", "test"),

    ("**bold**", "*bold*"),
    ("__bold__", "*bold*"),

    ("*italic*", "_\ritalic_\r"),
    ("_italic_", "_\ritalic_\r"),

    ("`code`", "`code`"),

    ("*test", "\\*test"),
    ("test*", "test\\*"),

    ("\\*test*", "\\*test\\*"),
    ("\\**test**", "\\*_\rtest_\r\\*"),
    ("\\*test*test*", "\\*test_\rtest_\r"),

    ("*test\\*", "\\*test\\*"),
    ("*test\\*test*", "_\rtest\\*test_\r"),

    ("\\\\test\\\\test\\\\", "\\\\test\\\\test\\\\"),

    ("**bold** and *italic*", "*bold* and _\ritalic_\r"),
    ("**bold** and _italic_", "*bold* and _\ritalic_\r"),
    ("__bold__ or *italic*", "*bold* or _\ritalic_\r"),
    ("__bold__ and _italic_ or `code`", "*bold* and _\ritalic_\r or `code`"),

    ("**bold**_italic_`code`", "*bold*_\ritalic_\r`code`"),
    ("**bold**`code`_italic_", "*bold*`code`_\ritalic_\r"),
    # ("_italic___bold__`code`", "_\ritalic_\r*bold*`code`"),
    ("_italic_`code`**bold**", "_\ritalic_\r`code`*bold*"),
    ("`code`_italic_**bold**", "`code`_\ritalic_\r*bold*"),
    ("`code`**bold***italic*", "`code`*bold*_\ritalic_\r"),

    ("* just a list item", "\\* just a list item"),
    ("escape * and _ here", "escape \\* and \\_ here"),
    ("not part of entity: *", "not part of entity: \\*"),
    ("unpaired _ in text", "unpaired \\_ in text"),
    # ("backtick ` outside code", "backtick \\` outside code"),

    ("**bold text with * star**", "*bold text with \\* star*"),
    ("**_ found inside bold text**", "*\\_ found inside bold text*"),
    ("*italic text with _*", "_\ritalic text with \\__\r"),
    ("``multiple backtick`s``", "`multiple backtick\\`s`"),
    ("`code with * and _`", "`code with \\* and \\_`"),
    ("_snake\\_case_", "_\rsnake\\_case_\r"),
    ("**2*2=4**", "*2\\*2\\=4*"),

    # ("*italic **bold***", "_italic *bold*_"),
    # ("**bold *italic* bold**", "*bold _italic_ bold*"),
    # ("*italic **bold** italic*", "_italic *bold* italic_"),

    ("`*not bold* _not italic_`", "`\\*not bold\\* \\_not italic\\_`"),

    ("preescaped: \\*", "preescaped: \\*"),
    ("\\*not bold\\*", "\\*not bold\\*"),
    ("it is \\_italic\\_", "it is \\_italic\\_"),
    ("\\`code\\` missing", "\\`code\\` missing"),

    ("***", "\\*\\*\\*"),
    ("****", "\\*\\*\\*\\*"),
    ("**", "\\*\\*"),
]


@pytest.mark.parametrize(("input_str", "output_str"), COMMONMARK_TO_TELEGRAMV2_TESTS)
@pytest.mark.asyncio
async def test_commonmark_to_telegramv2(input_str: str, output_str: str) -> None:
    async def _iter() -> AsyncIterator[str]:
        await asyncio.sleep(0.0)
        yield input_str
    assert "".join([_ async for _ in EscapeChars(_iter())]) == output_str
