from fastapi import Request, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from core.config import settings

security = HTTPBearer(auto_error=False)

async def get_current_user(request: Request) -> dict | None:
    """
    Validate Supabase JWT. Returns None for anonymous (honeypot allows).
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None  # Anonymous OK for honeypot routes
    
    try:
        scheme, token = auth_header.split()
        if scheme.lower() != "bearer":
            return None
        
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated",
            options={"verify_signature": True}
        )
        if payload.get("iss") != settings.SUPABASE_URL:
            raise HTTPException(status_code=401, detail="Invalid issuer")
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except (InvalidTokenError, jwt.InvalidTokenError):
        raise HTTPException(status_code=401, detail="Invalid token")

def require_admin(user: dict = Depends(get_current_user)):
    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return user

