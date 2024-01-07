import time

from typing import Tuple, Callable
from .configs import RateLimitHelper


class RateLimiter:
    """Rate limiter"""

    def __init__(self, config: RateLimitHelper, prefix: str = "rate_limiter") -> None:
        self.config = config
        self.prefix = prefix

    def resolve_key(self, key: str | None, key_builder: Callable | None, request, *args, **kwargs) -> str:
        """Get key"""
        if key:
            return key
        elif key_builder and callable(key_builder):
            return key_builder(request, *args, **kwargs)
        return "global"

    def request_rate_limiter(
        self,
        key: str,
        now: int,
        requested: int
    ) -> Tuple[bool, int]:
        raise NotImplemented

    def exceed_rate_limit(self, key: str | None, key_builder: Callable | None, request, *args, **kwargs) -> Tuple[bool, int]:
        """Check if rate limit exceeded"""
        key = self.resolve_key(key, key_builder, request, *args, **kwargs)
        allowed, tokens_left = self.request_rate_limiter(
            key, int(time.time()), 1
        )
        return not allowed, tokens_left

