from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

class SandboxCreateRequest(BaseModel):
    user_id: UUID
    env_type: str
    difficulty_level: int = 1

class SandboxCreateResponse(BaseModel):
    sandbox_id: UUID
    session_token: str
    env_type: str
    theme_template: str
    difficulty_level: int

class ScoreAttackRequest(BaseModel):
    sandbox_id: UUID
    session_token: str
    attack_payload: Dict[str, Any]
    attack_surface: str
    source_ip: str

class ScoreAttackResponse(BaseModel):
    attack_detected: bool
    attack_type: Optional[str] = None
    confidence: float = 0.0
    xp_earned: int = 0
    total_xp: int = 0
    level: int = 1
    level_up: bool = False
    badge_unlocked: Optional[str] = None
    hint: Optional[str] = None
