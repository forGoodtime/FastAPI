from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time

class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, get_redis, limit=5, window=60):
        super().__init__(app)
        self.get_redis = get_redis
        self.limit = limit
        self.window = window

    async def dispatch(self, request, call_next):
        redis = self.get_redis()
        if redis is None:
            # Redis не инициализирован (например, во время тестов) — пропускаем лимитирование
            return await call_next(request)

        client_ip = request.client.host
        key = f"rl:{client_ip}"
        now = int(time.time())
        window_start = now - (now % self.window)
        redis_key = f"{key}:{window_start}"

        count = await redis.get(redis_key)
        if count is None:
            await redis.set(redis_key, 1, ex=self.window)
            count = 1
        else:
            count = int(count) + 1
            await redis.set(redis_key, count, ex=self.window)

        if count > self.limit:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Try again later."}
            )

        return await call_next(request)