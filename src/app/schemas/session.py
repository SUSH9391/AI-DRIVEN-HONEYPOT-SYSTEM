from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID

class SessionCreate(BaseModel):
    ip: str
    fingerprint: Optional[Dict[str, Any]] = None

class SessionRead(SessionCreate):
    id: UUID
    started_at: datetime
    last_seen: datetime
    event_count: int
    is_blocked: bool

class SessionBlock(BaseModel):
    is_blocked: bool = True

