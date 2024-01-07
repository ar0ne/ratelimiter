from ninja import NinjaAPI

from app.api import router as api_router

from ratelimiter.exceptions import RateLimitExceededError

api = NinjaAPI()
api.add_router("/", api_router)


@api.exception_handler(RateLimitExceededError)
def rate_limit_error(request, exc):
    return api.create_response(
        request,
        {"message": exc.message},
        status=exc.status_code,
    )