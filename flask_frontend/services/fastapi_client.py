import httpx
from flask_frontend.config import Config
from typing import Dict, Any, Optional

class FastAPIClient:
    def __init__(self):
        self.base_url = Config.FASTAPI_INTERNAL_URL
        self.service_token = Config.FASTAPI_SERVICE_TOKEN

    async def _request(self, method: str, endpoint: str, jwt: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        headers = {
            "X-Service-Token": self.service_token,
        }
        if jwt:
            headers["Authorization"] = f"Bearer {jwt}"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method, 
                    f"{self.base_url}{endpoint}", 
                    headers=headers,
                    timeout=10.0,
                    **kwargs
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                return {"error": True, "detail": str(e), "status_code": e.response.status_code}
            except httpx.RequestError as e:
                return {"error": True, "detail": f"Connection error: {str(e)}"}

    # --- Auth endpoints (no JWT needed) ---

    async def register(self, email: str, password: str, username: str) -> Dict[str, Any]:
        return await self._request("POST", "/api/auth/register", json={
            "email": email,
            "password": password,
            "username": username
        })

    async def login(self, email: str, password: str) -> Dict[str, Any]:
        return await self._request("POST", "/api/auth/login", json={
            "email": email,
            "password": password
        })

    async def me(self, jwt: str) -> Dict[str, Any]:
        return await self._request("GET", "/api/auth/me", jwt=jwt)

    # --- Sandbox endpoints (JWT required) ---

    async def create_sandbox(self, env_type: str, difficulty_level: int = 1, jwt: Optional[str] = None) -> Dict[str, Any]:
        return await self._request("POST", "/api/sandbox/create", jwt=jwt, json={
            "env_type": env_type,
            "difficulty_level": difficulty_level
        })

    async def end_sandbox(self, sandbox_id: str, jwt: Optional[str] = None) -> Dict[str, Any]:
        return await self._request("DELETE", f"/api/sandbox/{sandbox_id}", jwt=jwt)

    async def get_sandbox_status(self, sandbox_id: str, jwt: Optional[str] = None) -> Dict[str, Any]:
        return await self._request("GET", f"/api/sandbox/{sandbox_id}/status", jwt=jwt)

    # --- Scoring endpoints (JWT required) ---

    async def score_attack(self, sandbox_id: str, session_token: str, payload: dict, surface: str, ip: str, jwt: Optional[str] = None) -> Dict[str, Any]:
        return await self._request("POST", "/api/detect/score", jwt=jwt, json={
            "sandbox_id": sandbox_id,
            "session_token": session_token,
            "attack_payload": payload,
            "attack_surface": surface,
            "source_ip": ip
        })

    # --- User endpoints (JWT required) ---

    async def get_user_stats(self, user_id: str, jwt: Optional[str] = None) -> Dict[str, Any]:
        return await self._request("GET", f"/api/user/{user_id}/stats", jwt=jwt)

    async def get_leaderboard(self) -> Dict[str, Any]:
        return await self._request("GET", "/api/leaderboard")

fastapi_client = FastAPIClient()
