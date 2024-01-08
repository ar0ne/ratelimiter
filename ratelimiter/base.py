import time

from typing import Tuple, Callable
from .configs import RateLimitHelper


class RateLimiter:
    """Rate limiter"""

    PREFIX = "rate_limiter"
    DEFAULT_KEY = "default"

    def __init__(self, config: RateLimitHelper, prefix: str | None = None) -> None:
        self.config = config
        self.prefix = prefix if prefix else self.PREFIX

    def resolve_key(self, key: str | None, key_builder: Callable | None, *args, **kwargs) -> str:
        """Get key"""
        if key:
            return key
        elif key_builder and callable(key_builder):
            return key_builder(*args, **kwargs)
        return self.DEFAULT_KEY

    def exceed_rate_limit(self, key: str, requested: int) -> Tuple[bool, int]:
        """
        Check if rate limit exceeded for the key.

        :param key: Check rate limits agains the key (e.g. user ID, IP address)
        :param requested: Indicates amount of new calls.
        :returns: A combination of was the limit exceeded and how many requests left.
        """
        return False, -1
