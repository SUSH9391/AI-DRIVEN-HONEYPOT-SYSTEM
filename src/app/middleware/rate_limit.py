from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from core.redis import redis_pool
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

limiter = Limiter(key_func=get_remote_address, storage_uri="redis://localhost:6379")
limiter.state.storage = redis_pool

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/api/admin"):
            # Admin 10/min
            response = await limiter.limiter.limit("10/minute")(request, call_next)
        else:
            # Honeypot 100/hour IP
            response = await limiter.limiter.limit("100/hour")(request, call_next)
        return response

