from fastapi import APIRouter
from prometheus_fastapi_instrumentator import Instrumentator

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check():
    return {"status": "healthy"}

instrumentator = Instrumentator().instrument_metrics()

@router.get("/metrics")
async def metrics():
    pass  # Prometheus scrapes /metrics

