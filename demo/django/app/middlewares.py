"""Demo middleware"""

from ratelimiter.exceptions import RateLimitExceededError
from config.rate_limits import rate_limiter


def FooHeaderRateLimiterMiddleware(get_response):
    """
    Example of middleware that check rate limits against some header.
    """
    def middleware(request):
        foo_header = request.headers.get("foo")
        if foo_header is not None:
            throttled, _ = rate_limiter.exceed_rate_limit(foo_header)
            if throttled:
                raise RateLimitExceededError
        return get_response(request)
    return middleware
