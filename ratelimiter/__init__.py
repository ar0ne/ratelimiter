import sys

version = '0.0.1'
__version__ = version


MIN_PYTHON_VERSION = 3, 8
MIN_PYTHON_VERSION_STR = '.'.join([str(v) for v in MIN_PYTHON_VERSION])

if sys.version_info < MIN_PYTHON_VERSION:
    raise Exception(f"Ratelimiter {version} requires Python {MIN_PYTHON_VERSION_STR} or newer.")
