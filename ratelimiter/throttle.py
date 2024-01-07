import logging
import redis
import time
import math
import functools
from typing import Tuple, Callable, List
from ratelimiter.exceptions import RateLimitExceededError
from django.http.response import HttpResponse
from redis.exceptions import WatchError

PREFIX = "request_rate_limiter:"

# How many requests per second do you want a user to be allowed to do?
REPLENISH_RATE = 5

# How much bursting do you want to allow?
CAPACITY = 5 * REPLENISH_RATE


log = logging.getLogger(__name__)


r = redis.Redis(host="127.0.0.1", port=6379, db=0)


class RateLimiter:
    """Rate limiter"""

    def __init__(self) -> None:
        pass



rate_limiter = RateLimiter()


def request_rate_limiter(
    token_key: str, 
    timestamp_key: str,
    rate: int,
    capacity: int,
    now: int,
    requested: int
) -> Tuple[bool, int]:
    """Checks if request is not exceeded rate limit"""

    pipe = r.pipeline()
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


def exceed_rate_limit(key: str) -> Tuple[bool, int]:
    """Check if rate limit exceeded"""
    token_key, timestamp_key = f"{PREFIX}{key}.tokens", f"{PREFIX}.{key}.timestamp"
    try:
        allowed, tokens_left = request_rate_limiter(
            token_key, timestamp_key, REPLENISH_RATE, CAPACITY, int(time.time()), 1
        )
    except redis.exceptions.RedisError as ex:
        log.warning("Redis failed, %s", ex, exc_info=True)
        return False, -1
    return not allowed, tokens_left


def get_bucket_key(key: str | None, key_builder: Callable | None, request, *args, **kwargs) -> str:
    """Get bucket key"""
    if key:
        return key
    elif key_builder and callable(key_builder):
        return key_builder(request, *args, **kwargs)
    return "global"


def with_rate_limit(key: str | None = None, key_builder: Callable | None = None):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(request, *args, **kwargs):
            bucket_key = get_bucket_key(key, key_builder, request, *args, **kwargs)
            throttled, _ = exceed_rate_limit(bucket_key)
            if throttled:
                raise RateLimitExceededError
            response = f(request, *args, **kwargs)
            return response
        return wrapper
    return decorator