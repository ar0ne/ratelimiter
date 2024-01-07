"""Exceptions"""

class RateLimitExceededError(Exception):
    """Rate limit exceeded error"""

    def __init__(self) -> None:
        """Init error"""
        self.status_code = 429
        self.message = "Rate limit exceeded"


class ServiceUnavailableError(Exception):
    pass
