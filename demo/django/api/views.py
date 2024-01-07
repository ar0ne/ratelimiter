import time
import random
from ninja import NinjaAPI
from .schemas import DummyResult
from asgiref.sync import sync_to_async

from ipware import get_client_ip

from ratelimiter.throttle import with_rate_limit

api = NinjaAPI()

"""
Critical methods
POSTs
GETs
Test mode traffic
"""

def cpu_bound(n: int) -> int:
    """compute something"""
    i = 0
    while i < 2 ** n:
        i += 1
    return i


def get_client_ip_from_request(request, *args, **kwargs):
    """Get client IP from request"""
    client_id = get_client_ip(request)
    return client_id[0]


@api.post("/critical", response={200: DummyResult})
@with_rate_limit(key_builder=get_client_ip_from_request)
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