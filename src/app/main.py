from fastapi import FastAPI, Request, BackgroundTasks, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.routers import honeypot, admin, health
from app.middleware import AuthMiddleware, FingerprintMiddleware, LoggingMiddleware
from app.middleware.rate_limit import limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from core.database import engine, Base
from prometheus_fastapi_instrumentator import Instrumentator
import uvicorn

# App factory
def create_app():
    app = FastAPI(title="AI Honeypot", version="1.0.0")
    
    # DB create tables (dev only)
    @app.on_event("startup")
    async def startup():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
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
    app.include_router(health.router)
    
    # Templates/static (reuse existing)
    templates = Jinja2Templates(directory="templates")
    app.mount("/static", StaticFiles(directory="static"), name="static")
    
    # Prometheus
    Instrumentator().instrument(app).expose(app)
    
    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

