
import time

import asyncio

import logging


log = logging.getLogger(__name__)


class Limiter:
    APICALL_LIMIT = 1

    MESSAGE_WINDOW = 60
    MESSAGE_EVENTS = 20

    def __init__(self) -> None:
        self._msg_stamps: list[float] = []
        self._last_apicall = 0.0
        self._lock = asyncio.Lock()

    def _log_msg(self, label: str) -> None:
        assert self._msg_stamps
        log.debug(
            "& %s %d %.2f %.2f", label, len(self._msg_stamps),
            self._msg_stamps[-1] - self._msg_stamps[0], self._msg_stamps[-1])

    async def wait_msg(self) -> bool:
        async with self._lock:
            current = time.monotonic()
            expired = current - self.MESSAGE_WINDOW

            while self._msg_stamps and self._msg_stamps[0] <= expired:
                self._msg_stamps.pop(0)

            barrier = current
            if len(self._msg_stamps) >= self.MESSAGE_EVENTS:
                barrier = self._msg_stamps[0] + self.MESSAGE_WINDOW
                await asyncio.sleep(barrier - current)

            self._msg_stamps.append(barrier)
            self._log_msg("wait msg")

            return True

    async def wait_api(self) -> bool:
        async with self._lock:
            barrier = self._last_apicall + self.APICALL_LIMIT

            await asyncio.sleep(barrier - time.monotonic())
            self._last_apicall = time.monotonic()
            # self._log_call("wait api", self._last_apicall)

            return True

    async def test(self) -> bool:
        async with self._lock:
            if self._last_apicall + self.APICALL_LIMIT <= time.monotonic():
                self._last_apicall = time.monotonic()
                # self._log_call("test api", self._last_apicall)
                return True

            return False
