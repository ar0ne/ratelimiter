import random
import time

import redis
from asgiref.sync import sync_to_async
from ninja import Router

from config.rate_limits import rate_limiter

from .decorators import with_rate_limit
from .schemas import DummyResult

router = Router()


"""
Critical methods
POSTs
GETs
Test mode traffic
"""


def cpu_bound(n: int) -> int:
    """compute something"""
    i = 0
    while i < 2**n:
        i += 1
    return i


def get_rate_limit_name_for_critical_request(*args, **kwargs):
    """Get client IP from request if user is not authenticated"""
    request = args[0]
    if not request.user.is_authenticated:
        return "critical_anonymous"
    return "critical"


@router.post("/critical", response={200: DummyResult})
@with_rate_limit(rate_limiter, key_builder=get_rate_limit_name_for_critical_request)
def critical(request):
    """Do something critical here"""
    result = cpu_bound(random.randrange(10))
    return {"result": result}


@router.post("/important", response={200: DummyResult})
def important(request):
    """Do something important here"""
    result = cpu_bound(random.randrange(10))
    return {"result": result}


@router.get("/normal", response={200: DummyResult})
def normal(request):
    """Do something usual here"""
    result = cpu_bound(random.randrange(10))
    return {"result": result}


@router.post("/async/critical")
async def async_critical(request):
    return await sync_to_async(critical(request))
