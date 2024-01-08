import functools
from typing import Callable

from ratelimiter.base import RateLimiter
from ratelimiter.exceptions import RateLimitExceededError


def with_rate_limit(
    rate_limiter: RateLimiter,
    key: str | None = None,
    key_builder: Callable | None = None,
):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            bucket = rate_limiter.resolve_key(
                key, key_builder, request, *args, **kwargs
            )
            throttled, _ = rate_limiter.exceed_rate_limit(bucket, 1)
            if throttled:
                raise RateLimitExceededError
            response = func(request, *args, **kwargs)
            # we could set to header amount of requests that are left for the bucket
            #
            return response

        return wrapper

    return decorator
