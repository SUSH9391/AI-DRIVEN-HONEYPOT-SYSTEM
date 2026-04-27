from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_session
from core.config import settings
from app.models.attack_log import User
from app.core.dependencies import require_service_token, get_current_user
from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid
import httpx

router = APIRouter(prefix="/api/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    username: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    user_id: uuid.UUID
    username: Optional[str]
    email: str
    role: str
    jwt: str
    total_xp: Optional[int] = None
    level: Optional[int] = None


class MeResponse(BaseModel):
    user_id: uuid.UUID
    username: Optional[str]
    email: str
    role: str
    total_xp: int
    level: int


async def _supabase_auth_request(path: str, payload: dict) -> dict:
    """Helper to call Supabase Auth REST API."""
    url = f"{settings.SUPABASE_URL}/auth/v1/{path}"
    headers = {
        "apikey": settings.SUPABASE_ANON_KEY,
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        if response.status_code >= 400:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.json().get("msg", "Supabase auth error")
            )
        return response.json()


@router.post("/register", response_model=AuthResponse)
async def register(
    req: RegisterRequest,
    db: AsyncSession = Depends(get_session),
    _token: str = Depends(require_service_token),
):
    # 1. Create user in Supabase Auth
    sb_resp = await _supabase_auth_request(
        "signup",
        {
            "email": req.email,
            "password": req.password,
            "data": {"username": req.username},
        },
    )
    sb_user = sb_resp.get("user")
    if not sb_user:
        raise HTTPException(status_code=500, detail="Supabase user creation failed")

    supabase_uid = sb_user["id"]
    jwt_token = sb_resp.get("access_token", sb_resp.get("session", {}).get("access_token", ""))

    # 2. Create row in public.users
    new_user = User(
        id=uuid.uuid4(),
        email=req.email,
        username=req.username,
        supabase_uid=supabase_uid,
        role="user",
        total_xp=0,
        level=1,
    )
    db.add(new_user)
    await db.commit()

    return AuthResponse(
        user_id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        role=new_user.role,
        jwt=jwt_token,
        total_xp=new_user.total_xp,
        level=new_user.level,
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    req: LoginRequest,
    db: AsyncSession = Depends(get_session),
    _token: str = Depends(require_service_token),
):
    # 1. Authenticate via Supabase
    sb_resp = await _supabase_auth_request(
        "token?grant_type=password",
        {
            "email": req.email,
            "password": req.password,
        },
    )
    sb_user = sb_resp.get("user")
    if not sb_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    supabase_uid = sb_user["id"]
    jwt_token = sb_resp.get("access_token", sb_resp.get("session", {}).get("access_token", ""))

    # 2. Fetch user row from public.users
    result = await db.execute(
        select(User).where(User.supabase_uid == supabase_uid)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found in local DB")

    return AuthResponse(
        user_id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        jwt=jwt_token,
        total_xp=user.total_xp,
        level=user.level,
    )


@router.get("/me", response_model=MeResponse)
async def me(
    current_user: User = Depends(get_current_user),
):
    return MeResponse(
        user_id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role,
        total_xp=current_user.total_xp,
        level=current_user.level,
    )
