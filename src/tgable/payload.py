
from abc import ABC, abstractmethod

from dataclasses import dataclass, field

from enum import StrEnum

from typing import override


@dataclass
class Payload(ABC):

    @property
    def as_type(self) -> str:
        clsname = self.__class__.__name__
        if not clsname.endswith("Payload"):
            raise ValueError
        return clsname.removesuffix("Payload").lower()

    @abstractmethod
    def __str__(self) -> str:
        ...


@dataclass
class UnknownPayload(Payload):
    @override
    def __str__(self) -> str:
        return ""


@dataclass
class CommandPayload(Payload):
    message: str
    cmdline: str = field(init=False)
    command: str = field(init=False)
    options: list[str] = field(init=False)
    mention: str | None = field(init=False)
    content: str | None = field(init=False)

    def __post_init__(self) -> None:
        if not self.message.startswith("/"):
            raise ValueError

        self.cmdline, _, self.content = self.message.partition("\n")
        if not self.content:
            self.content = None

        self.command, *_ = self.cmdline.split(maxsplit=1)
        self.options = self.cmdline.removeprefix(self.command).strip().split()

        self.command, _, self.mention = self.command.partition("@")
        if not self.mention:
            self.mention = None

        _, _, self.command = self.command.partition("/")

    @override
    def __str__(self) -> str:
        length = ""
        if self.content is not None:
            length = f" length={len(self.content)}"
        return f"command={self.cmdline}" + length


@dataclass
class KeyboardPayload(CommandPayload):
    keyboard: str = ""
    version: str = ""

    @override
    def __str__(self) -> str:
        return f"version={self.version} keyboard={self.keyboard} command={self.cmdline}"


@dataclass
class MessagePayload(Payload):
    content: str

    @override
    def __str__(self) -> str:
        return f"length={len(self.content)}"


class DocumentPayloadType(StrEnum):
    ANIMATION = "animation"
    AUDIO = "audio"
    DOCUMENT = "document"
    PAID_MEDIA = "paid_media"
    PHOTO = "photo"
    VIDEO = "video"
    VIDEO_NOTE = "video_note"
    VOICE = "voice"


@dataclass
class DocumentPayload(Payload):
    content: str | None
    document: DocumentPayloadType

    @override
    def __str__(self) -> str:
        length = ""
        if self.content is not None:
            length = f" length={len(self.content)}"
        return f"document={self.document}" + length


class ServicePayloadType(StrEnum):
    CREATED = "created"
    CLOSED = "closed"
    EDITED = "edited"
    REOPENED = "reopened"


@dataclass
class ServicePayload(Payload):
    service: ServicePayloadType
    caption: str | None = None

    @override
    def __str__(self) -> str:
        caption = ""
        if self.caption is not None:
            caption = f" caption={self.caption}"
        return f"service={self.service}" + caption


class MyMemberPayloadType(StrEnum):
    UNKNOWN = "unknown"
    INVITED = "invited"


@dataclass
class MyMemberPayload(Payload):
    mymember: MyMemberPayloadType
    old_status: str
    new_status: str
    caption: str | None = None

    @override
    def __str__(self) -> str:
        caption = ""
        if self.caption is not None:
            caption = f" caption={self.caption}"
        return f"mymember={self.mymember} old={self.old_status} new={self.new_status}" + caption


@dataclass
class CheckoutPayload(Payload):
    amount: int
    invoice: str

    @override
    def __str__(self) -> str:
        return f"amount={self.amount} invoice={self.invoice}"


@dataclass
class PaymentPayload(Payload):
    amount: int
    invoice: str

    @override
    def __str__(self) -> str:
        return f"amount={self.amount} invoice={self.invoice}"
