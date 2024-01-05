import time
import random
from ninja import NinjaAPI
from .schemas import DummyResult

api = NinjaAPI()

"""
Critical methods
POSTs
GETs
Test mode traffic
"""

def cpu_bounded_operation(n: int) -> int:
    """computate something"""
    i = 0
    while i < 2 ** n:
        i += 1
    return i


@api.post("/critical", response={200: DummyResult})
def critical(request):
    """Do something critical here"""
    result = cpu_bounded_operation(random.randrange(100))
    return {"result": result}

@api.post("/important", response={200: DummyResult})
def important(request):
    """Do something important here"""
    result = cpu_bounded_operation(random.randrange(50))
    return {"result": result}

@api.get("/normal", response={200: DummyResult})
def normal(request):
    """Do something usual here"""
    result = cpu_bounded_operation(random.randrange(20))
    return {"result": result}
