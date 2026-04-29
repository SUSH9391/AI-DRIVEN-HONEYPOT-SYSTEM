from fastapi import Security, HTTPException, status, Request
from fastapi.security.api_key import APIKeyHeader
from core.config import settings
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse

api_key_header = APIKeyHeader(name="X-Service-Token", auto_error=True)

async def verify_service_token(api_key: str = Security(api_key_header)):
    if api_key != settings.FASTAPI_SERVICE_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid service token"
        )
    return api_key

class ServiceAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        public_paths = {"/docs", "/openapi.json", "/health", "/api/auth/login", "/api/auth/register"}
        if request.url.path in public_paths:
            return await call_next(request)
        
        token = request.headers.get("X-Service-Token")
        if token != settings.FASTAPI_SERVICE_TOKEN:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "Invalid service token"}
            )
            
        return await call_next(request)
