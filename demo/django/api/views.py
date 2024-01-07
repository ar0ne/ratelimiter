import time
import random
import redis

from ninja import NinjaAPI
from .schemas import DummyResult
from asgiref.sync import sync_to_async

from ipware import get_client_ip

from ratelimiter.decorators import with_rate_limit
from ratelimiter.redis import RedisRateLimiter
from ratelimiter.configs import limits
from ratelimiter.exceptions import RateLimitExceededError

from django.core.cache import cache

api = NinjaAPI()

@api.exception_handler(RateLimitExceededError)
def service_unavailable(request, exc):
    return api.create_response(
        request,
        {"message": exc.message},
        status=exc.status_code,
    )


"""
Critical methods
POSTs
GETs
Test mode traffic
"""

r = redis.Redis(host="127.0.0.1", port=6379, db=0)

limits.set_config({
    "critical": (5, 25),
    "critical_anonymous": (1, 5),
    "default": (50, 250),
})

rate_limiter = RedisRateLimiter(conn=r, config=limits, prefix="rate_limits")


def cpu_bound(n: int) -> int:
    """compute something"""
    i = 0
    while i < 2 ** n:
        i += 1
    return i

def get_ip(request) -> str:
    return get_client_ip(request)[0]

def get_rate_limit_name_for_critical_request(*args, **kwargs):
    """Get client IP from request if user is not authenticated"""
    request = args[0]
    if not request.user.is_authenticated:
        return "critical_anonymous"
    return "critical"

@api.post("/critical", response={200: DummyResult})
@with_rate_limit(rate_limiter, key_builder=get_rate_limit_name_for_critical_request)
def critical(request):
    """Do something critical here"""
    result = cpu_bound(random.randrange(10))
    return {"result": result}

@api.post("/important", response={200: DummyResult})
def important(request):
    """Do something important here"""
    result = cpu_bound(random.randrange(10))
    return {"result": result}

@api.get("/normal", response={200: DummyResult})
def normal(request):
    """Do something usual here"""
    result = cpu_bound(random.randrange(10))
    return {"result": result}

@api.post("/async/critical")
async def async_critical(request):
    return await sync_to_async(critical(request))