"""In-memory sliding window rate limiter for PhishGuard API.

Guarantees fair usage and protects the service from denial of service (DoS)
without external service dependencies.
"""

from __future__ import annotations

import collections
import time
from typing import Optional

from fastapi import HTTPException, Request, status


class InMemoryRateLimiter:
    """Sliding-window rate limiter per client IP."""

    def __init__(self, requests_per_minute: int = 60, enabled: bool = True):
        self.requests_per_minute = requests_per_minute
        self.enabled = enabled
        self._history: dict[str, collections.deque[float]] = collections.defaultdict(collections.deque)

    def get_client_ip(self, request: Request) -> str:
        """Extract client IP, checking X-Forwarded-For if behind a proxy."""
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            # First IP in the comma-separated list is the client IP
            return forwarded.split(",")[0].strip()
        if request.client and request.client.host:
            return request.client.host
        return "127.0.0.1"

    def check(self, request: Request) -> None:
        """Evaluate rate limit for incoming request. Raises 429 if limit exceeded."""
        if not self.enabled:
            return

        ip = self.get_client_ip(request)
        now = time.monotonic()
        window_start = now - 60.0

        records = self._history[ip]

        # Evict timestamps outside the 60-second window
        while records and records[0] < window_start:
            records.popleft()

        if len(records) >= self.requests_per_minute:
            retry_after = int(max(1.0, 60.0 - (now - records[0])))
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Batas permintaan terlampaui (maksimal {self.requests_per_minute} req/menit). Coba lagi dalam {retry_after} detik.",
                headers={"Retry-After": str(retry_after)},
            )

        records.append(now)

    def reset(self) -> None:
        """Clear all rate limiting history."""
        self._history.clear()


# Default global rate limiter instance (60 req/min)
limiter = InMemoryRateLimiter(requests_per_minute=60)

