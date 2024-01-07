"""Demo middleware"""

from ratelimiter.exceptions import RateLimitExceededError


class HeaderRateLimitMiddleware(MiddlewareMixin):

   def process_request(self, request):
        """
        Example of middleware that check rate limits against some header.
        """

        foo_header = request.headers.get("foo")
        if foo_header is not None:
            pass
            

