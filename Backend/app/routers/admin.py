from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.security import require_admin
from core.database import get_session
from app.models.attack_log import AttackLog
from app.schemas.attack import AttackLogRead
from app.services.session_service import SessionService
from typing import List

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.get("/attacks", response_model=List[AttackLogRead])
async def list_attacks(
    db: AsyncSession = Depends(get_session),
    limit: int = Query(50, le=100),
    offset: int = Query(0),
    type: str = Query(None),
    user = Depends(require_admin)
):
    query = select(AttackLog).order_by(AttackLog.created_at.desc()).limit(limit).offset(offset)
    if type:
        query = query.where(AttackLog.attack_type == type)
    result = await db.execute(query)
    attacks = result.scalars().all()
    return attacks

@router.get("/attacks/{attack_id}", response_model=AttackLogRead)
async def get_attack(attack_id: str, db: AsyncSession = Depends(get_session), user = Depends(require_admin)):
    attack = await db.get(AttackLog, attack_id)
    if not attack:
        raise HTTPException(status_code=404)
    return attack

@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_session), user = Depends(require_admin)):
    # Aggregated metrics
    result = await db.execute(select(AttackLog.attack_type, func.count()).group_by(AttackLog.attack_type))
    stats = result.fetchall()
    return {"attack_types": dict(stats)}

@router.get("/sessions")
async def list_sessions(session_svc: SessionService = Depends(), user = Depends(require_admin)):
    # Redis sessions stub
    return {"sessions": []}  # Implement later

@router.delete("/sessions/{ip}")
async def block_session(ip: str, session_svc: SessionService = Depends(), user = Depends(require_admin)):
    await session_svc.block_ip(ip)
    return {"blocked": ip}

