import threading
import time

import redis
from fastapi import Request

from app.core.config import get_settings
from app.core.errors import AppError
from app.core.redis_client import get_redis

_local: dict[str, tuple[int, float]] = {}
_lock = threading.Lock()


def client_ip(request: Request) -> str:
    """Behind a reverse proxy, run uvicorn with --proxy-headers and --forwarded-allow-ips."""
    return request.client.host if request.client else "unknown"


def _hit_redis(key: str, window: int) -> tuple[int, int]:
    pipe = get_redis().pipeline()
    pipe.set(key, 0, ex=window, nx=True)
    pipe.incr(key)
    pipe.ttl(key)
    _, count, ttl = pipe.execute()
    return int(count), max(int(ttl), 1)


def _hit_local(key: str, window: int) -> tuple[int, int]:
    """Per-process fallback when Redis is unreachable. Limits are then per worker only."""
    now = time.monotonic()
    with _lock:
        if len(_local) > 10000:
            for k in [k for k, (_, reset) in _local.items() if reset <= now]:
                _local.pop(k, None)
        count, reset = _local.get(key, (0, 0.0))
        if now >= reset:
            count, reset = 0, now + window
        count += 1
        _local[key] = (count, reset)
        return count, int(reset - now) + 1


class RateLimiter:
    def __init__(self, scope: str, limit: int, window_seconds: int) -> None:
        self.scope = scope
        self.limit = limit
        self.window = window_seconds

    def check(self, identifier: str) -> None:
        if not get_settings().rate_limit_enabled:
            return
        key = f"artifactx:rl:{self.scope}:{identifier}"
        try:
            count, ttl = _hit_redis(key, self.window)
        except redis.RedisError:
            count, ttl = _hit_local(key, self.window)
        if count > self.limit:
            raise AppError(
                429,
                "rate_limited",
                "Too many requests. Please try again later.",
                headers={"Retry-After": str(ttl)},
            )

    def __call__(self, request: Request) -> None:
        self.check(client_ip(request))
