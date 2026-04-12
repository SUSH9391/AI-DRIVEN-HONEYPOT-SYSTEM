import uuid
from typing import Dict, Any, Optional
from core.redis import get_redis
from app.schemas.session import SessionCreate

class SessionService:
    TTL_HOURS = 24

    async def get_or_create_session(self, ip: str, fingerprint: Dict[str, Any] = None) -> str:
        redis = await get_redis().__anext__()
        session_key = f"session:{ip}"
        session_id = await redis.get(session_key)
        if session_id:
            return session_id
        
        # Create new
        session_id = str(uuid.uuid4())
        data = SessionCreate(ip=ip, fingerprint=fingerprint).dict()
        await redis.set(session_key, session_id, ex=self.TTL_HOURS * 3600)
        await redis.hset(f"session_data:{session_id}", mapping=data)
        await redis.expire(f"session_data:{session_id}", self.TTL_HOURS * 3600)
        return session_id

    async def increment_event_count(self, session_id: str):
        redis = await get_redis().__anext__()
        await redis.hincrby(f"session_data:{session_id}", "event_count", 1)
        await redis.expire(f"session_data:{session_id}", self.TTL_HOURS * 3600)

    async def block_ip(self, ip: str):
        redis = await get_redis().__anext__()
        session_key = f"session:{ip}"
        await redis.set(session_key, "BLOCKED", ex=self.TTL_HOURS * 3600)

    async def is_blocked(self, ip: str) -> bool:
        redis = await get_redis().__anext__()
        session_key = f"session:{ip}"
        value = await redis.get(session_key)
        return value == "BLOCKED"

