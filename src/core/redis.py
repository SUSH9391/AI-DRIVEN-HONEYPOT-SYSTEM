
import redis.asyncio as aredis

aredis_client = aredis.Redis(host="redis", port=6379, decode_responses=True)

async def get_redis():
    return aredis_client

