import httpx
from config import Config
from typing import Dict, Any

class FastAPIClient:
    def __init__(self):
        self.base_url = Config.FASTAPI_INTERNAL_URL
        self.headers = {"X-Service-Token": Config.FASTAPI_SERVICE_TOKEN}

    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method, 
                    f"{self.base_url}{endpoint}", 
                    headers=self.headers,
                    timeout=10.0,
                    **kwargs
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                return {"error": True, "detail": str(e), "status_code": e.response.status_code}
            except httpx.RequestError as e:
                return {"error": True, "detail": f"Connection error: {str(e)}"}

    async def create_sandbox(self, user_id: str, env_type: str, difficulty_level: int = 1) -> Dict[str, Any]:
        return await self._request("POST", "/api/sandbox/create", json={
            "user_id": user_id,
            "env_type": env_type,
            "difficulty_level": difficulty_level
        })

    async def end_sandbox(self, sandbox_id: str) -> Dict[str, Any]:
        return await self._request("DELETE", f"/api/sandbox/{sandbox_id}")

    async def score_attack(self, sandbox_id: str, session_token: str, payload: dict, surface: str, ip: str) -> Dict[str, Any]:
        return await self._request("POST", "/api/detect/score", json={
            "sandbox_id": sandbox_id,
            "session_token": session_token,
            "attack_payload": payload,
            "attack_surface": surface,
            "source_ip": ip
        })

    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        return await self._request("GET", f"/api/user/{user_id}/stats")

    async def get_leaderboard(self) -> Dict[str, Any]:
        return await self._request("GET", "/api/leaderboard")

    async def login_with_supabase(self, email: str, password: str) -> Dict[str, Any]:
        # Simulating external Supabase auth that internal FastAPI verifies for this architecture
        # For our architecture it just stores the token in Flask session directly
        return {"jwt": "fake_jwt", "user_id": "00000000-0000-0000-0000-000000000000", "username": "admin"}

    async def signup_with_supabase(self, email: str, password: str, username: str) -> Dict[str, Any]:
        return {"jwt": "fake_jwt", "user_id": "00000000-0000-0000-0000-000000000000", "username": username}

fastapi_client = FastAPIClient()
