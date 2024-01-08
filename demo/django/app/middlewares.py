"""Demo middleware"""

from ratelimiter.exceptions import RateLimitExceededError

from config.rate_limits import rate_limiter


def FooHeaderRateLimiterMiddleware(get_response):
    """
    Example of middleware that check rate limits against some header.
    """

    def middleware(request):
        # it could be auth header, User-Agent, URL
        foo_header = request.headers.get("foo")
        if foo_header is not None:
            bucket = "foo" if foo_header == "bar" else "not_foo"
            throttled, _ = rate_limiter.exceed_rate_limit(bucket, 1)
            if throttled:
                raise RateLimitExceededError
        return get_response(request)

    return middleware
