from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from core.database import get_session
from core.redis import aredis_client
from app.models.attack_log import User, AttackLog
from app.models.sandbox import Badge
import uuid
from app.middleware.service_auth import verify_service_token
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/api", tags=["users"], dependencies=[Depends(verify_service_token)])

@router.get("/user/{user_id}/stats")
async def get_user_stats(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Users can only view their own stats
    if str(user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to view this user's stats")
        
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    badge_res = await db.execute(select(Badge).where(Badge.user_id == user_id))
    badges = [b.badge_type for b in badge_res.scalars().all()]
    
    attacks_res = await db.execute(
        select(AttackLog).where(AttackLog.user_id == user_id).order_by(desc(AttackLog.created_at)).limit(20)
    )
    recent_attacks = attacks_res.scalars().all()
    
    rank = await aredis_client.zrevrank("leaderboard:global", str(user_id))
    leaderboard_rank = rank + 1 if rank is not None else -1
    
    return {
        "username": user.username,
        "total_xp": user.total_xp,
        "level": user.level,
        "badges": badges,
        "attack_history": [
            {
                "attack_type": a.attack_type,
                "confidence": a.confidence,
                "xp_earned": a.xp_earned,
                "created_at": a.created_at,
                "path": a.path
            }
            for a in recent_attacks
        ], 
        "leaderboard_rank": leaderboard_rank
    }

@router.get("/leaderboard")
async def get_leaderboard(db: AsyncSession = Depends(get_session)):
    top_entries = await aredis_client.zrevrange("leaderboard:global", 0, 19, withscores=True)
    
    if not top_entries:
        return []
        
    user_ids = [uuid.UUID(uid) for uid, score in top_entries]
    
    users_res = await db.execute(select(User).where(User.id.in_(user_ids)))
    users_dict = {str(u.id): {"username": u.username, "level": u.level} for u in users_res.scalars().all()}
    
    leaderboard = []
    for uid_str, score in top_entries:
        u_info = users_dict.get(uid_str, {"username": "Unknown", "level": 1})
        leaderboard.append({
            "username": u_info["username"],
            "total_xp": int(score),
            "level": u_info["level"]
        })
        
    return leaderboard
