import pytest

def test_login_page_renders(client):
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b"Welcome Back" in response.data

def test_signup_page_renders(client):
    response = client.get('/auth/signup')
    assert response.status_code == 200
    assert b"Join the Nexus" in response.data

def test_login_redirects_on_success(client, mock_fastapi_client):
    response = client.post('/auth/login', data={'email': 'y@y.com', 'password': 'pass'})
    assert response.status_code == 302
    assert '/dashboard' in response.headers['Location']
    mock_fastapi_client.login_with_supabase.assert_called_once_with('y@y.com', 'pass')

def test_login_shows_error_on_failure(client, mock_fastapi_client):
    from unittest.mock import AsyncMock
    mock_fastapi_client.login_with_supabase = AsyncMock(return_value={"error": True, "detail": "Invalid credentials"})
    
    response = client.post('/auth/login', data={'email': 'y@y.com', 'password': 'wrong'})
    # Assuming standard flask flashes re-render or follow redirects.
    assert response.status_code == 200 # Flashed message renders in template
    assert b"Invalid credentials" in response.data
