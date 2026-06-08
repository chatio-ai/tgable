
from tgable.content.telegramv2 import escape_text


def text(message: str) -> str:
    return (
        "\n".join(">" + escape_text(line.strip()) for line in message.splitlines())
    ) + "\n"


def link(caption: str, url: str) -> str:
    return f"> [{caption}]({url})"


def log(message: str, level: str | None = None) -> str:
    if level is None:
        level = 'text'
    return f">```{level}\n" + (
        "\n".join(escape_text(line.strip()) for line in message.splitlines()).strip()
    ) + "```\n"


def exc(exc_value: Exception) -> str:
    return log(f"{type(exc_value).__name__}: {exc_value}", level='error')


def info(message: str) -> str:
    return log(message, level='info')


def warn(message: str) -> str:
    return log(message, level='warn')


def error(message: str) -> str:
    return log(message, level='error')
