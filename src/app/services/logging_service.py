import json
from datetime import datetime
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.attack_log import AttackLog
from app.schemas.attack import AttackLogCreate
from core.database import get_session

class LoggingService:
    def __init__(self, log_file: str = "attack_logs.json"):
        self.log_file = log_file

    async def write_attack(self, data: Dict[str, Any], rule_result, fake_resp, db: AsyncSession = None):
        """
        Dual-write: PG + NDJSON file.
        """
        # PG write
        if db:
            log_create = AttackLogCreate(
                ip=data.get("ip"),
                user_agent=data.get("user_agent"),
                method=data.get("method", "POST"),
                path=data.get("path"),
                query=data.get("query"),
                body=data.get("body"),
                attack_type=rule_result.attack_type,
                confidence=rule_result.confidence,
                rule_matched=rule_result.rule_matched,
                fake_response=fake_resp
            )
            log = AttackLog(**log_create.dict())
            db.add(log)
            await db.commit()
        
        # NDJSON fallback
        log_entry = {
            **log_create.dict(),
            "created_at": datetime.utcnow().isoformat()
        }
        with open(self.log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

