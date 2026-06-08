
from dataclasses import dataclass

from tgable.payload import Payload
from tgable.request import Request
from tgable.channel import Channel


@dataclass(frozen=True)
class Context[PayloadT: Payload, ServiceT]:
    request: Request[PayloadT]
    channel: Channel
    service: ServiceT
