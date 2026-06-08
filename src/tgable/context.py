
from dataclasses import dataclass

from tgable.payload import Payload
from tgable.request import Request
from tgable.channel import Channel


# pylint: disable=too-few-public-methods
@dataclass(frozen=True)
class Service:
    pass


@dataclass(frozen=True)
class Context[PayloadT: Payload, ServiceT: Service]:
    request: Request[PayloadT]
    channel: Channel
    service: ServiceT
