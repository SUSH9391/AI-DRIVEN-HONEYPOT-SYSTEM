from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID

class AttackLogCreate(BaseModel):
    ip: str
    user_agent: Optional[str] = None
    method: str
    path: str
    query: Optional[str] = None
    body: Optional[Dict[str, Any]] = None
    attack_type: Optional[str] = None
    confidence: Optional[float] = None
    rule_matched: Optional[str] = None
    fake_response: Optional[Dict[str, Any]] = None
    session_id: Optional[UUID] = None

class AttackLogRead(AttackLogCreate):
    id: UUID
    created_at: datetime
    country: Optional[str] = None
    asn: Optional[str] = None

class AttackLogUpdate(BaseModel):
    country: Optional[str] = None
    asn: Optional[str] = None

