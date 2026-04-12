import aioredis
from core.config import settings

redis_pool = aioredis.from_url(settings.REDIS_URL, decode_responses=True)

async def get_redis():
    redis = await redis_pool
    try:
        yield redis
    finally:
        # Pools are managed, no close needed
        pass

