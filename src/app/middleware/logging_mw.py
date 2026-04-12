from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
import ujson as json

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        response: Response = await call_next(request)
        
        process_time = time.time() - start_time
        log_data = {
            "method": request.method,
            "path": request.url.path,
            "ip": request.client.host,
            "user_agent": request.headers.get("user-agent"),
            "status_code": response.status_code,
            "process_time": process_time,
            "size": len(response.body or b"")
        }
        
        # Structured log to console (Prometheus/ELK later)
        print(json.dumps(log_data))
        
        return response

