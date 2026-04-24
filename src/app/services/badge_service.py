from core.database import async_session
from sqlalchemy import select, func
from app.models.attack_log import AttackLog
from app.models.sandbox import Badge
import uuid

BADGE_RULES = {
    "first_blood":   lambda stats: stats.get("total_attacks", 0) >= 1,
    "sql_slinger":   lambda stats: stats.get("sqli_count", 0) >= 5,
    "script_kiddie": lambda stats: stats.get("xss_count", 0) >= 5,
    "card_shark":    lambda stats: stats.get("carding_count", 0) >= 3,
    "ghost_walker":  lambda stats: stats.get("path_traversal_count", 0) >= 3,
    "streak":        lambda stats: stats.get("session_streak", 0) >= 3,
}

async def check_and_award_badges(user_id: str, sandbox_id: str, attack_type: str):
    async with async_session() as db:
        user_uuid = uuid.UUID(user_id)
        
        total_attacks = await db.scalar(select(func.count()).select_from(AttackLog).where(AttackLog.user_id == user_uuid))
        sqli_count = await db.scalar(select(func.count()).select_from(AttackLog).where(AttackLog.user_id == user_uuid, AttackLog.attack_type == 'sqli'))
        xss_count = await db.scalar(select(func.count()).select_from(AttackLog).where(AttackLog.user_id == user_uuid, AttackLog.attack_type == 'xss'))
        carding_count = await db.scalar(select(func.count()).select_from(AttackLog).where(AttackLog.user_id == user_uuid, AttackLog.attack_type == 'carding'))
        path_traversal_count = await db.scalar(select(func.count()).select_from(AttackLog).where(AttackLog.user_id == user_uuid, AttackLog.attack_type == 'path_traversal'))
        
        stats = {
            "total_attacks": total_attacks or 0,
            "sqli_count": sqli_count or 0,
            "xss_count": xss_count or 0,
            "carding_count": carding_count or 0,
            "path_traversal_count": path_traversal_count or 0,
            "session_streak": 3 
        }
        
        existing_badges_res = await db.execute(select(Badge.badge_type).where(Badge.user_id == user_uuid))
        existing_badges = set(existing_badges_res.scalars().all())
        
        awarded = []
        for badge, rule in BADGE_RULES.items():
            if badge not in existing_badges and rule(stats):
                new_badge = Badge(
                    id=uuid.uuid4(),
                    user_id=user_uuid,
                    badge_type=badge
                )
                db.add(new_badge)
                awarded.append(badge)
                
        if awarded:
            await db.commit()
            
        return awarded
