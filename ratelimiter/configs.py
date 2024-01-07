from typing import Dict, Tuple

from copy import deepcopy


Limit = Tuple[int, int]

class RateLimitHelper:
    """
    Configure rate limits. Configs contains next data:
    {
        "limit_name": (rate: int, capacity: int)
    }
    # rate - How many requests per second do you want a user to be allowed to do?
    # capacity - How much bursting do you want to allow?
    """

    _default: Dict[str, Dict[str, Limit]] = {
        "default": (100, 500)
    }

    def __init__(self):
        """Init helper"""
        self._limits = {**self._default}

    def add(self, name: str, limit: Limit) -> None:
        """
        Add a limit to the current config. If the limit already exists, it
        will overwrite it::

            >>> limits.add("anonymous", (1000, 5000))
            
        :param config: Mapping containing the limits configuration
        """
        self._limits[name] = limit

    def get_config(self):
        """
        Return copy of current stored config
        """
        return deepcopy(self._limits)

    def get_limits(self, name: str) -> object:
        """Get limits by name or default"""
        if name in self._limits.keys():
            return self._limits[name]
        return self._limits["default"]

    def set_config(self, config):
        if "default" not in config:
            raise ValueError("default config must be provided")
        for limit_name in config.keys():
            self._limits.pop(limit_name, None)
        self._limits = config


limits = RateLimitHelper()
