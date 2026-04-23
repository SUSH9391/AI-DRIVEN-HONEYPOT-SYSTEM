from fastapi import FastAPI, Request

from app.routers import honeypot, admin, health, sandbox, scoring, users
from app.middleware import AuthMiddleware, FingerprintMiddleware, LoggingMiddleware
from app.middleware.rate_limit import limiter

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from core.database import engine, Base
from prometheus_fastapi_instrumentator import Instrumentator

import uvicorn
import os


# App factory
def create_app():
    app = FastAPI(title="AI Honeypot", version="1.0.0")

    # App is now JSON-only backend. (Jinja2 moved to Flask frontend)

    # DB create tables (dev only)
    @app.on_event("startup")
    async def startup():
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        except Exception as e:
            print(f"DB init failed (continuing): {e}")

    # Middleware stack
    app.add_middleware(AuthMiddleware)
    app.add_middleware(FingerprintMiddleware)
    app.add_middleware(LoggingMiddleware)

    # Rate Limiter Global
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Routers
    app.include_router(honeypot.router)
    app.include_router(admin.router)
    @app.get("/health")
    async def health():
        return {"status": "ok"}
    app.include_router(sandbox.router)
    app.include_router(scoring.router)
    app.include_router(users.router)

    # (All UI routes moved to Flask frontend)

    # Prometheus Monitoring
    Instrumentator().instrument(app).expose(app)

    return app


# Create app instance
app = create_app()


# Run locally
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

