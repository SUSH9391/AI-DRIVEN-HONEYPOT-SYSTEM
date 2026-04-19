from fastapi import FastAPI, Request
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
import os


# App factory
def create_app():
    app = FastAPI(title="AI Honeypot", version="1.0.0")

    # ✅ BASE DIR FIX (IMPORTANT)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # ✅ Templates & Static (FIXED PATHS)
    templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
    app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

    # Share templates across routers
    app.state.templates = templates

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

    # ---------------------------
    # 🌐 Frontend Routes (HTML)
    # ---------------------------

    @app.get("/")
    async def root(request: Request):
        return templates.TemplateResponse("login.html", {"request": request})

    @app.get("/signup")
    async def signup_page(request: Request):
        return templates.TemplateResponse("signup.html", {"request": request})

    @app.get("/product")
    async def product_page(request: Request):
        return templates.TemplateResponse("product.html", {"request": request})

    @app.get("/checkout")
    async def checkout_page(request: Request):
        return templates.TemplateResponse("checkout.html", {"request": request})

    @app.get("/admin_login")
    async def admin_login_page(request: Request):
        return templates.TemplateResponse("admin_login.html", {"request": request})

    @app.get("/dashboard")
    async def dashboard_page(request: Request):
        return templates.TemplateResponse("dashboard.html", {"request": request})

    # Prometheus Monitoring
    Instrumentator().instrument(app).expose(app)

    return app


# Create app instance
app = create_app()


# Run locally
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)