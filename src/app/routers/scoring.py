from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_session
from core.redis import aredis_client
import uuid
import json
import asyncio
from app.models.sandbox import SandboxSession, Badge
from app.models.attack_log import User, AttackLog
from app.schemas.sandbox import ScoreAttackRequest, ScoreAttackResponse
from app.middleware.service_auth import verify_service_token
from app.core.dependencies import get_current_user
from app.services.honeypot_service import get_honeypot_service, HoneypotService
from app.services.badge_service import check_and_award_badges
from core.config import settings
from datetime import datetime

router = APIRouter(prefix="/api/detect", tags=["scoring"], dependencies=[Depends(verify_service_token)])

@router.post("/score", response_model=ScoreAttackResponse)
async def score_attack(
    req: ScoreAttackRequest, 
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_session),
    honeypot_svc: HoneypotService = Depends(get_honeypot_service),
    current_user: User = Depends(get_current_user)
):
    # Validate session_token against Redis
    expected_sandbox_id = await aredis_client.get(f"sandbox:{req.session_token}")
    if not expected_sandbox_id or expected_sandbox_id != str(req.sandbox_id):
        raise HTTPException(status_code=403, detail="Invalid session token")

    # Validate Sandbox in DB
    result = await db.execute(select(SandboxSession).where(SandboxSession.id == req.sandbox_id))
    sandbox = result.scalar_one_or_none()
    
    if not sandbox or not sandbox.active:
        raise HTTPException(status_code=404, detail="Active sandbox session not found")
    
    # Ensure the sandbox belongs to the authenticated user
    if sandbox.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to score this sandbox")
        
    rule_res = honeypot_svc.rule_detector.classify(json.dumps(req.attack_payload))
    confidence = rule_res.confidence
    
    if settings.USE_ML_DETECTOR and honeypot_svc.ml_detector:
        ml_conf = await asyncio.to_thread(honeypot_svc.ml_detector.score, req.attack_payload)
        confidence = max(confidence, ml_conf)
        
    attack_detected = confidence > 0.0
    
    xp_earned = 0
    level_up = False
    badge_unlocked = None
    attack_type = rule_res.attack_types[0] if rule_res.attack_types else "Unknown"
    
    if attack_detected:
        xp_earned = round(confidence * 100)
        
        if sandbox.difficulty_level >= 5 and confidence <= 0.75:
            xp_earned = 0 
            
        if xp_earned > 0:
            sandbox.xp_earned += xp_earned
            sandbox.attacks_detected += 1
            
            user_res = await db.execute(select(User).where(User.id == sandbox.user_id))
            user = user_res.scalar_one_or_none()
            if user:
                user.total_xp += xp_earned
                
                old_level = user.level
                if user.total_xp >= 2000:
                    new_lvl = 5 + ((user.total_xp - 2000) // 1000)
                elif user.total_xp >= 1000:
                    new_lvl = 4
                elif user.total_xp >= 500:
                    new_lvl = 3
                elif user.total_xp >= 200:
                    new_lvl = 2
                else:
                    new_lvl = 1
                    
                if new_lvl > old_level:
                    user.level = new_lvl
                    level_up = True
                    badge_unlocked = "Level Up"

                # Update Redis leaderboard
                await aredis_client.zadd("leaderboard:global", {str(user.id): user.total_xp})

                # Background task for badges
                background_tasks.add_task(check_and_award_badges, str(user.id), str(sandbox.id), attack_type)
            
            # Log attack
            log_entry = AttackLog(
                id=uuid.uuid4(),
                ip=req.source_ip,
                attack_type=attack_type,
                body=req.attack_payload,
                path=req.attack_surface,
                method="POST",
                user_agent="",
                confidence=confidence,
                sandbox_id=sandbox.id,
                user_id=sandbox.user_id,
                xp_earned=xp_earned,
                created_at=datetime.utcnow()
            )
            db.add(log_entry)

            await db.commit()
            
            hint = None
            if sandbox.difficulty_level < 3:
                hint = f"Great! Your payload scored {confidence*100}% confidence."
            
            return ScoreAttackResponse(
                attack_detected=True,
                attack_type=attack_type,
                confidence=confidence,
                xp_earned=xp_earned,
                total_xp=user.total_xp if user else 0,
                level=user.level if user else 1,
                level_up=level_up,
                badge_unlocked=badge_unlocked,
                hint=hint
            )

    return ScoreAttackResponse(attack_detected=False)
