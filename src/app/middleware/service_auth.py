from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from core.config import settings

api_key_header = APIKeyHeader(name="X-Service-Token", auto_error=True)

async def verify_service_token(api_key: str = Security(api_key_header)):
    if api_key != settings.FASTAPI_SERVICE_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid service token"
        )
    return api_key
