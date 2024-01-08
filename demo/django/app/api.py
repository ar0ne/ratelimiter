import random
import time

import redis
from asgiref.sync import sync_to_async
from ninja import Router, Schema

from config.rate_limits import rate_limiter

from .decorators import ratelimit


class DummyResult(Schema):
    result: int


router = Router()

def cpu_bound(n: int) -> int:
    """compute something"""
    i = 0
    while i < 2**n:
        i += 1
    return i


# You could use generalized solution with middleware
# Or additionaly specify rate limit policy for endpoint
# 
# @ratelimit(rate_limiter, key_builder=get_rate_limit_name_for_critical_request)
@router.post("/foo", response={200: DummyResult})
def foo(request):
    """Do something useful here"""
    result = cpu_bound(random.randrange(10))
    return {"result": result}
