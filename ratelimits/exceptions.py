"""Exceptions"""
from ninja.errors import HttpError

class RateLimitExceeded(HttpError):
    """Rate limit exceeded"""

    def __init__(self, status_code: int | None = None, message: str | None = None) -> None:
        """Init error"""
        status_code = status_code or 429
        message = message or "Rate limit exceeded"
        super().__init__(status_code, message)


class ServiceUnavailableError(Exception):
    pass
