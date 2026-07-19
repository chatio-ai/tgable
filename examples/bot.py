#!/usr/bin/env python

import os
import asyncio

import logging

from tgable.payload import Payload
from tgable.context import Context
from tgable.factory import Factory
from tgable.dispatch import Feature
from tgable.dispatch import Dispatch
from tgable.gateway import Gateway


logging.basicConfig()
logging.getLogger('tgable').setLevel(logging.DEBUG)


async def text_message(context: Context[Payload, None], content: str) -> None:
    await context.channel.message_reply(content)


feature = Feature[None]()
feature.message()(text_message)


if __name__ == '__main__':
    asyncio.run(Gateway(
        bot_key=os.environ['BOT_API_KEY'],
        web_app=os.environ.get('BOT_WEB_APP'),
        factory=Factory(service_factory=lambda _: None),
        dispatch=Dispatch(feature),
    ).serve())
