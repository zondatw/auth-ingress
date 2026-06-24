from __future__ import annotations

from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from threading import Lock


class FailedSignInLimiter:
    def __init__(self, attempts: int, window_seconds: int):
        self.attempts = attempts
        self.window = timedelta(seconds=window_seconds)
        self._events: dict[str, deque[datetime]] = defaultdict(deque)
        self._lock = Lock()

    def _prune(self, key: str, now: datetime) -> None:
        events = self._events[key]
        while events and now - events[0] >= self.window:
            events.popleft()
        if not events:
            self._events.pop(key, None)

    def blocked(self, *keys: str, now: datetime | None = None) -> bool:
        current = now or datetime.now(timezone.utc)
        with self._lock:
            for key in keys:
                self._prune(key, current)
                if len(self._events.get(key, ())) >= self.attempts:
                    return True
        return False

    def failure(self, *keys: str, now: datetime | None = None) -> None:
        current = now or datetime.now(timezone.utc)
        with self._lock:
            for key in keys:
                self._prune(key, current)
                self._events[key].append(current)

    def success(self, *keys: str) -> None:
        with self._lock:
            for key in keys:
                self._events.pop(key, None)


class ManagementRequestLimiter(FailedSignInLimiter):
    def allow(self, key: str, *, now: datetime | None = None) -> bool:
        if self.blocked(key, now=now):
            return False
        self.failure(key, now=now)
        return True
