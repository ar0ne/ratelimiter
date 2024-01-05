import time
import random
from ninja import NinjaAPI
from .schemas import DummyResult
from asgiref.sync import sync_to_async

from ratelimits.throttle import rate_limit

api = NinjaAPI()

"""
Critical methods
POSTs
GETs
Test mode traffic
"""

def cpu_bounded_operation(n: int) -> int:
    """compute something"""
    i = 0
    while i < 2 ** n:
        i += 1
    return i


@api.post("/critical", response={200: DummyResult})
@rate_limit()
def critical(request):
    """Do something critical here"""
    result = cpu_bounded_operation(random.randrange(10))
    return {"result": result}

@api.post("/important", response={200: DummyResult})
def important(request):
    """Do something important here"""
    result = cpu_bounded_operation(random.randrange(10))
    return {"result": result}

@api.get("/normal", response={200: DummyResult})
def normal(request):
    """Do something usual here"""
    result = cpu_bounded_operation(random.randrange(10))
    return {"result": result}

@api.post("/async/critical")
async def async_critical(request):
    return await sync_to_async(critical(request))