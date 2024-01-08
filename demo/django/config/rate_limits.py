import redis
from ratelimiter.configs import limits
from ratelimiter.redis import RedisRateLimiter

from django.conf import settings

r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

limits.set_config(settings.RATE_LIMITS)

rate_limiter = RedisRateLimiter(
    conn=r, config=limits, prefix=settings.RATE_LIMIT_PREFIX
)
