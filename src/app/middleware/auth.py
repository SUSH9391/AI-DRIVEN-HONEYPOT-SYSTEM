from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from core.security import get_current_user

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip public routes
        public_paths = {"/docs", "/openapi.json", "/health"}
        if request.url.path in public_paths:
            response = await call_next(request)
            return response
        
        # Add user to request.state for honeypot (anon OK)
        try:
            request.state.user = await get_current_user(request)
        except HTTPException:
            request.state.user = None
        
        # Block non-admin on real admin routes
        if request.url.path.startswith("/api/admin") and not request.state.user:
            raise HTTPException(status_code=403, detail="Admin JWT required")
        
        response = await call_next(request)
        return response

