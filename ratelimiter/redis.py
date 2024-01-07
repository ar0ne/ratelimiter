import redis
import math
import logging

from typing import Callable, Tuple
from redis.exceptions import WatchError

from ratelimiter.base import RateLimiter


log = logging.getLogger(__name__)

class RedisRateLimiter(RateLimiter):
    """Redis rate limiter"""

    def __init__(
        self, 
        conn,
        config: dict,
        prefix: str | None = None
    ) -> None:
        super().__init__(config, prefix)
        self.conn = conn

    def get_token_key(self, key: str) -> str:
        return f"{self.prefix}::{key}::token"

    def get_timestamp_key(self, key: str) -> str:
        return f"{self.prefix}::{key}::timestamp"

    def request_rate_limiter(
        self,
        key: str,
        now: int,
        requested: int
    ) -> Tuple[bool, int]:
        """Checks if request is not exceeded rate limit"""

        token_key, timestamp_key = self.get_token_key(key), self.get_timestamp_key(key)
        limits = self.config.get_limits(key)
        rate, capacity = limits.get("rate"), limits.get("capacity")

        pipe = self.conn.pipeline()
        while True:
            try:
                pipe.watch(token_key, timestamp_key)

                fill_time = capacity / rate
                ttl = math.floor(fill_time * 2)

                last_token = int(pipe.get(token_key) or capacity)
                last_refreshed = int(pipe.get(timestamp_key) or 0)

                delta = max(0, now - last_refreshed)
                filled_tokens = min(capacity, last_token + delta * rate)
                allowed = filled_tokens >= requested
                new_tokens = filled_tokens
                if allowed:
                    new_tokens = filled_tokens - requested

                pipe.multi()
                pipe.set(token_key, new_tokens, ex=ttl)
                pipe.set(timestamp_key, now, ex=ttl)
                pipe.execute()

                return allowed, new_tokens
            except WatchError:
                log.info("oups watch error")
                continue
            finally:
                pipe.reset()

    def exceed_rate_limit(self, key: str | None, key_builder: Callable | None, request, *args, **kwargs) -> Tuple[bool, int]:
        try:
            return super().exceed_rate_limit(key, key_builder, request, *args, **kwargs)
        except redis.exceptions.RedisError as ex:
            log.warning("Redis failed, %s", ex, exc_info=True)
            return False, -1