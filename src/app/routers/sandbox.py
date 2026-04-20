from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from core.database import get_session
import uuid
import secrets
import random
from app.models.sandbox import SandboxSession
from app.schemas.sandbox import SandboxCreateRequest, SandboxCreateResponse
from app.middleware.service_auth import verify_service_token

router = APIRouter(prefix="/api/sandbox", tags=["sandbox"], dependencies=[Depends(verify_service_token)])

THEMES = {
    "sqli": ["sqli/banking_login.html", "sqli/corporate_portal.html"],
    "xss": ["xss/social_feed.html", "xss/forum.html"],
    "carding": ["carding/ecomm_checkout.html", "carding/gift_card_store.html"],
    "path_traversal": ["path_traversal/file_manager.html", "path_traversal/admin_panel.html"]
}

@router.post("/create", response_model=SandboxCreateResponse)
async def create_sandbox(req: SandboxCreateRequest, db: AsyncSession = Depends(get_session)):
    if req.env_type not in THEMES:
        raise HTTPException(status_code=400, detail="Invalid env_type")

    theme_template = random.choice(THEMES[req.env_type])
    sandbox_id = uuid.uuid4()
    session_token = secrets.token_hex(32)

    new_session = SandboxSession(
        id=sandbox_id,
        user_id=req.user_id,
        env_type=req.env_type,
        theme_template=theme_template,
        difficulty_level=req.difficulty_level,
        active=True
    )
    
    db.add(new_session)
    await db.commit()
    
    return SandboxCreateResponse(
        sandbox_id=sandbox_id,
        session_token=session_token,
        env_type=req.env_type,
        theme_template=theme_template,
        difficulty_level=req.difficulty_level
    )

@router.delete("/{sandbox_id}")
async def delete_sandbox(sandbox_id: uuid.UUID, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(SandboxSession).where(SandboxSession.id == sandbox_id))
    sandbox = result.scalar_one_or_none()
    
    if not sandbox or not sandbox.active:
        raise HTTPException(status_code=404, detail="Active sandbox not found")
        
    sandbox.active = False
    sandbox.ended_at = func.now()
    await db.commit()
    
    return {
        "success": True, 
        "xp_summary": sandbox.xp_earned, 
        "attacks_detected": sandbox.attacks_detected
    }

@router.get("/{sandbox_id}/status")
async def get_sandbox_status(sandbox_id: uuid.UUID, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(SandboxSession).where(SandboxSession.id == sandbox_id))
    sandbox = result.scalar_one_or_none()
    
    if not sandbox:
        raise HTTPException(status_code=404, detail="Sandbox not found")
        
    return {
        "active": sandbox.active,
        "attacks_detected": sandbox.attacks_detected,
        "xp_earned": sandbox.xp_earned,
        "current_streak": 0
    }
