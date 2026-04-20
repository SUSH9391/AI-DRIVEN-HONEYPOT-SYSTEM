import pytest
from unittest.mock import AsyncMock
from flask_frontend.app import create_app

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SECRET_KEY": "test_secret_key",
        "SESSION_TYPE": "null" # simplify for testing to memory dict basically
    })
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def mock_fastapi_client(mocker):
    # Mock the singleton instance in the services module
    mocked_client = mocker.patch("flask_frontend.routes.auth.fastapi_client", autospec=True)
    mocker.patch("flask_frontend.routes.dashboard.fastapi_client", new=mocked_client)
    mocker.patch("flask_frontend.routes.environments.fastapi_client", new=mocked_client)
    mocker.patch("flask_frontend.routes.sandbox.fastapi_client", new=mocked_client)
    # Set default async returns
    mocked_client.get_user_stats = AsyncMock(return_value={"total_xp": 100, "level": 1, "badges": []})
    mocked_client.login_with_supabase = AsyncMock(return_value={"jwt": "test", "user_id": "u-123", "username": "test"})
    return mocked_client

@pytest.fixture
def mock_httpx_fastapi_client(mocker):
    # Just mock the _request inside the actual class
    mocked_client = mocker.patch("flask_frontend.services.fastapi_client.FastAPIClient._request", new_callable=AsyncMock)
    return mocked_client

@pytest.fixture
def auth_client(client):
    with client.session_transaction() as sess:
        sess['user_id'] = "u-123"
        sess['username'] = "testuser"
        sess['jwt'] = "token"
    return client
