from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from core.database import get_session
from app.models.attack_log import User
from app.models.sandbox import Badge
import uuid
from app.middleware.service_auth import verify_service_token

router = APIRouter(prefix="/api", tags=["users"], dependencies=[Depends(verify_service_token)])

@router.get("/user/{user_id}/stats")
async def get_user_stats(user_id: uuid.UUID, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    badge_res = await db.execute(select(Badge).where(Badge.user_id == user_id))
    badges = [b.badge_type for b in badge_res.scalars().all()]
    
    return {
        "username": user.username,
        "total_xp": user.total_xp,
        "level": user.level,
        "badges": badges,
        "attack_history": [], 
        "leaderboard_rank": 1 
    }

@router.get("/leaderboard")
async def get_leaderboard(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(User).order_by(desc(User.total_xp)).limit(20))
    users = result.scalars().all()
    return [{"username": u.username, "total_xp": u.total_xp, "level": u.level} for u in users]
