import pytest
from app import create_app

@pytest.fixture
def app(tmp_path_factory):
    from cachelib.file import FileSystemCache
    test_app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key-32-chars-minimum!",
        "SESSION_TYPE": "cachelib",
        "SESSION_CACHELIB": FileSystemCache(
            str(tmp_path_factory.mktemp("sessions")), threshold=500
        ),
        "SESSION_PERMANENT": False,
        "WTF_CSRF_ENABLED": False,
        "FASTAPI_INTERNAL_URL": "http://mock-fastapi:8000",
        "FASTAPI_SERVICE_TOKEN": "test-token",
    })
    yield test_app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def mock_fastapi_client(monkeypatch):
    """
    Patches all methods on the FastAPIClient using pytest's built-in
    monkeypatch — no pytest-mock mocker needed as fallback.
    Uses unittest.mock.AsyncMock for async methods.
    """
    from unittest.mock import AsyncMock, patch
    from services import fastapi_client as fc_module

    mock = AsyncMock()
    mock.login_with_supabase.return_value = {
        "jwt": "fake-jwt",
        "user_id": "user-uuid-123",
        "username": "testuser"
    }
    mock.signup_with_supabase.return_value = {
        "jwt": "fake-jwt",
        "user_id": "user-uuid-123",
        "username": "testuser"
    }
    mock.get_user_stats.return_value = {
        "total_xp": 150,
        "level": 1,
        "badges": [],
        "recent_attacks": [],
        "leaderboard_rank": 42
    }
    mock.create_sandbox.return_value = {
        "sandbox_id": "sandbox-uuid-456",
        "session_token": "sandbox-token",
        "env_type": "sqli",
        "theme_template": "sqli/banking_login.html",
        "difficulty_level": 1
    }
    mock.score_attack.return_value = {
        "attack_detected": True,
        "attack_type": "sqli",
        "confidence": 0.92,
        "xp_earned": 92,
        "total_xp": 242,
        "level": 2,
        "level_up": False,
        "badge_unlocked": None,
        "hint": "Try using UNION SELECT next"
    }

    with patch.object(fc_module, "fastapi_client", mock):
        yield mock

@pytest.fixture
def mock_httpx_fastapi_client(monkeypatch):
    """Patches the internal _request method of FastAPIClient directly."""
    from unittest.mock import AsyncMock, patch
    from services.fastapi_client import FastAPIClient

    mock_request = AsyncMock()
    with patch.object(FastAPIClient, "_request", mock_request):
        yield mock_request

@pytest.fixture
def auth_client(app, client):
    with client.session_transaction() as sess:
        sess["user_id"] = "u-123"
        sess["username"] = "testuser"
        sess["level"] = 1
        sess["total_xp"] = 0
        sess["jwt"] = "fake-jwt-token"
    return client
