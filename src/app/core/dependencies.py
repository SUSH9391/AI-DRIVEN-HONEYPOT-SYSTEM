from fastapi import Header, HTTPException, Depends
from core.config import settings
from core.database import get_session
from app.models.attack_log import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import jwt as pyjwt


async def require_service_token(
    x_service_token: str = Header(...)
):
    if x_service_token != settings.FASTAPI_SERVICE_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid service token")


async def get_current_user(
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_session)
) -> User:
    """
    Validates Supabase JWT and returns User from DB.
    Used for routes that need to know WHO is calling.
    """
    try:
        token = authorization.replace("Bearer ", "")
        payload = pyjwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            options={"verify_aud": False}
        )
        supabase_uid = payload.get("sub")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    result = await db.execute(
        select(User).where(User.supabase_uid == supabase_uid)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def require_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """Only allows users with role='admin'."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
