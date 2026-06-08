
from typing import override

from aiogram.types import Message
from aiogram.types import User
from aiogram.types import Chat

from tgable.unicode import decode_text

from tgable.content.commonmark import reconstruct

from tgable.metadata import Objects

from tgable.payload import Payload
from tgable.payload import UnknownPayload
from tgable.payload import MessagePayload
from tgable.payload import CommandPayload
from tgable.payload import ServicePayload
from tgable.payload import ServicePayloadType
from tgable.payload import DocumentPayload
from tgable.payload import DocumentPayloadType
from tgable.payload import PaymentPayload

from . import Parsing


PRIVACY_THRESHOLD = 2


def _content_from_message(message: Message, *, caption: bool = False) -> str | None:
    if caption:
        contents = message.caption
        entities = message.caption_entities
    else:
        contents = message.text
        entities = message.entities

    if contents is None:
        return None

    if entities is None:
        entities = []

    if contents:
        contents = reconstruct(contents, entities).strip()
        contents = decode_text(contents)

    return contents


class MessageParsing(Parsing[Message]):

    @property
    @override
    def _object_id(self) -> str:
        return str(self._event.message_id)

    @property
    @override
    def _flow(self) -> Objects:
        return Objects(
            last_message_id=self._event.message_id,
        )

    @property
    @override
    def _user(self) -> User:
        assert self._event.from_user is not None
        return self._event.from_user

    @property
    @override
    def _chat(self) -> Chat:
        return self._event.chat

    @property
    @override
    def _thread_id(self) -> int | None:
        return self._event.message_thread_id

    @property
    def _service(self) -> ServicePayload | None:
        if self._event.forum_topic_created is not None:
            return ServicePayload(ServicePayloadType.CREATED, self._event.forum_topic_created.name)

        if self._event.forum_topic_closed is not None:
            return ServicePayload(ServicePayloadType.CLOSED)

        if self._event.forum_topic_edited is not None:
            return ServicePayload(ServicePayloadType.EDITED, self._event.forum_topic_edited.name)

        if self._event.forum_topic_reopened is not None:
            return ServicePayload(ServicePayloadType.REOPENED)

        return None

    @property
    def _document(self) -> DocumentPayloadType | None:
        document = None
        if self._event.animation is not None:
            document = DocumentPayloadType.ANIMATION
        if self._event.audio is not None:
            document = DocumentPayloadType.AUDIO
        if self._event.document is not None:
            document = DocumentPayloadType.DOCUMENT
        if self._event.paid_media is not None:
            document = DocumentPayloadType.PAID_MEDIA
        if self._event.photo is not None:
            document = DocumentPayloadType.PHOTO
        if self._event.video is not None:
            document = DocumentPayloadType.VIDEO
        if self._event.video_note is not None:
            document = DocumentPayloadType.VIDEO_NOTE
        if self._event.voice is not None:
            document = DocumentPayloadType.VOICE

        return document

    @property
    @override
    def _payload(self) -> Payload:

        if self._event.successful_payment is not None:
            return PaymentPayload(
                amount=self._event.successful_payment.total_amount,
                invoice=self._event.successful_payment.invoice_payload,
            )

        service = self._service
        if service is not None:
            return service

        document = self._document
        if document is not None:
            content = _content_from_message(self._event, caption=True)
            return DocumentPayload(content, document)

        content = _content_from_message(self._event)
        if content is None:
            return UnknownPayload()

        if content.startswith('/'):
            return CommandPayload(content)

        return MessagePayload(content)
