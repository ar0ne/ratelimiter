"""Redis rate limiter"""
import redis
import math
import time
import logging

from typing import Tuple

from ratelimiter.base import RateLimiter


log = logging.getLogger(__name__)

class RedisRateLimiter(RateLimiter):
    """Redis rate limiter"""

    def __init__(
        self, 
        conn: redis.Redis,
        config: dict,
        prefix: str | None = None
    ) -> None:
        """Init redis rate limiter"""
        super().__init__(config, prefix)
        self.conn = conn

    def exceed_rate_limit(self, key: str, requested: int) -> Tuple[bool, int]:
        """
        Check if rate limit exceeded for key.
        """
        try:
            return self._request_rate_limiter(key, requested)
        except redis.exceptions.RedisError as ex:
            # if redis error occurred, do not block request
            log.warning("Redis failed, %s", ex, exc_info=True)
            return False, -1

    def _get_token_key(self, key: str) -> str:
        """
        Build token key.
        """
        return f"{self.prefix}::{key}::token"

    def _get_timestamp_key(self, key: str) -> str:
        """
        Build timestamp key.
        """
        return f"{self.prefix}::{key}::timestamp"

    def _request_rate_limiter(self, key: str, requested: int) -> Tuple[bool, int]:
        """
        This is basic token bucket algorithm that relies on "check-and-set" with "WATCH" command in Redis.
        Another solution is to use Lua scripts which are atomic.
        """
        token_key, timestamp_key = self._get_token_key(key), self._get_timestamp_key(key)
        rate, capacity = self.config.get_limits(key)
        now = int(time.time())

        pipe = self.conn.pipeline()
        while True:
            try:
                # before the transaction, read values
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

                # start transcation
                pipe.multi()
                pipe.set(token_key, new_tokens, ex=ttl)
                pipe.set(timestamp_key, now, ex=ttl)
                # write it all together
                pipe.execute()

                return not allowed, new_tokens
            except redis.exceptions.WatchError:
                # if value was changed before we "commit" transaction, start again
                log.info("oups watch error")
                continue
            finally:
                pipe.reset()
