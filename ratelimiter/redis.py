import redis
from redis.exceptions import WatchError

r = redis.Redis(host="127.0.0.1", port=6379)

def atomic_get_set(key):
    with r.pipeline() as pipe:
        try:
            pipe.watch(key)
            pipe.multi()
            pipe.set(key, F())
            pipe.get(key)
            return pipe.execute()[-1]
        except WatchError:
            continue

# def request_rate_limiter(key):
