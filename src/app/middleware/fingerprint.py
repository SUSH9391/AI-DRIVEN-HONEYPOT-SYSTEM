import hashlib
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Any
import ujson as json

class FingerprintMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Simple fingerprint: UA + headers hash + TLS
        fingerprint_data = {
            "user_agent": request.headers.get("user-agent", ""),
            "accept": request.headers.get("accept", ""),
            "headers_hash": hashlib.md5(str(sorted(request.headers.items())).encode()).hexdigest()[:16]
        }
        request.state.fingerprint = fingerprint_data
        
        response = await call_next(request)
        return response

