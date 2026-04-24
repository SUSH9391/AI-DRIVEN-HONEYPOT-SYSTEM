from fastapi import APIRouter, Depends, Query, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.middleware.rate_limit import limiter
from core.security import require_admin
from core.database import get_session
from app.models.attack_log import AttackLog
from app.models.sandbox import SandboxSession
from app.schemas.attack import AttackLogRead
from app.middleware.service_auth import verify_service_token
from typing import List

router = APIRouter(prefix="/api/admin", tags=["admin"], dependencies=[Depends(verify_service_token)])

@router.get("/attacks", response_model=List[AttackLogRead])
@limiter.limit("10/minute")
async def list_attacks(
    request: Request,
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
@limiter.limit("10/minute")
async def get_attack(request: Request, attack_id: str, db: AsyncSession = Depends(get_session), user = Depends(require_admin)):
    attack = await db.get(AttackLog, attack_id)
    if not attack:
        raise HTTPException(status_code=404)
    return attack

@router.get("/stats")
@limiter.limit("10/minute")
async def get_stats(request: Request, db: AsyncSession = Depends(get_session), user = Depends(require_admin)):
    # Aggregated metrics
    result = await db.execute(select(AttackLog.attack_type, func.count()).group_by(AttackLog.attack_type))
    attack_types = dict(result.fetchall())
    
    total_detections_res = await db.execute(select(func.count()).select_from(AttackLog))
    total_detections = total_detections_res.scalar() or 0
    
    active_sandboxes_res = await db.execute(select(func.count()).select_from(SandboxSession).where(SandboxSession.active == True))
    active_sandboxes = active_sandboxes_res.scalar() or 0

    return {
        "attack_types": attack_types,
        "total_detections": total_detections,
        "active_sandboxes": active_sandboxes
    }

