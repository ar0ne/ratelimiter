from typing import Dict 

from copy import deepcopy

REPLENISH_RATE = 5
CAPACITY = 5 * REPLENISH_RATE


class RateLimitHelper:
    _config: Dict[str, Dict[str, int | str]] = {
        "default": {
            # How much bursting do you want to allow?
            "capacity": CAPACITY,
            # How many requests per second do you want a user to be allowed to do?
            "rate": REPLENISH_RATE,
        }
    }

    def __init__(self):
        """Init helper"""
        self._limits = {**self._config}

    def add(self, name: str, limit: Dict[str, object]) -> None:
        """
        Add a limit to the current config. If the limit already exists, it
        will overwrite it::

            >>> limits.add('default', {
                    "critical": {
                        "rate": 100,
                        "capacity": 500,
                    }
                })

        :param config: Mapping containing the limits configuration
        """
        self._config[name] = limit

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
