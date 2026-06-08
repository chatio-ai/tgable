
from collections.abc import Callable

from tgable.metadata import Binding

from tgable.locking import Locking
from tgable.limiter import Limiter
from tgable.context import Service


class Factory[ServiceT: Service]:

    def __init__(
        self,
        service_factory: Callable[[Binding], ServiceT],
    ) -> None:
        self._service_factory = service_factory

        self._locking_cache: dict[tuple[Binding.ChatId, Binding.ThreadId], Locking] = {}

        self._limiter_cache: dict[tuple[Binding.BotId, Binding.ChatId], Limiter] = {}

    def locking(self, binding: Binding) -> Locking:
        locking_key = (binding.chat_id, binding.thread_id)
        if self._locking_cache.get(locking_key) is None:
            self._locking_cache[locking_key] = Locking()
        return self._locking_cache[(binding.chat_id, binding.thread_id)]

    def limiter(self, binding: Binding) -> Limiter:
        limiter_key = (binding.bot_id, binding.chat_id)
        if self._limiter_cache.get(limiter_key) is None:
            self._limiter_cache[limiter_key] = Limiter()
        return self._limiter_cache[limiter_key]

    def service(self, binding: Binding) -> ServiceT:
        return self._service_factory(binding)
