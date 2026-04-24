from unittest.mock import AsyncMock

def test_sandbox_create_calls_fastapi(auth_client, mock_fastapi_client):
    mock_fastapi_client.create_sandbox = AsyncMock(return_value={"sandbox_id": "123", "theme_template": "sqli/banking_login.html"})
    
    response = auth_client.post('/sandbox/create', data={'env_type': 'sqli'})
    assert response.status_code == 302
    assert '/sandbox/play' in response.headers['Location']
    mock_fastapi_client.create_sandbox.assert_called_once()

def test_sandbox_play_renders_correct_template(auth_client):
    with auth_client.session_transaction() as sess:
        sess['active_sandbox'] = {"sandbox_id": "123", "theme_template": "sqli/banking_login.html"}
        
    response = auth_client.get('/sandbox/play')
    assert response.status_code == 200
    assert b"NorthWest Federal Bank" in response.data

def test_attack_scoring_returns_overlay(auth_client, mock_fastapi_client):
    with auth_client.session_transaction() as sess:
        sess['active_sandbox'] = {
            "sandbox_id": "123", 
            "session_token": "abc", 
            "theme_template": "sqli/banking_login.html"
        }
        
    mock_fastapi_client.score_attack = AsyncMock(return_value={"attack_detected": True, "xp_earned": 100, "confidence": 0.8})
    
    response = auth_client.post('/sandbox/attack', data={'username': "' OR 1=1 --", "password": "x"})
    assert response.status_code == 200
    assert b"Attack Detected!" in response.data
    assert b"+100 XP" in response.data

def test_level_up_flash_on_level_up(auth_client, mock_fastapi_client):
    with auth_client.session_transaction() as sess:
        sess['active_sandbox'] = {
            "sandbox_id": "123", 
            "session_token": "abc", 
            "theme_template": "sqli/banking_login.html"
        }
        
    mock_fastapi_client.score_attack = AsyncMock(return_value={"attack_detected": True, "level_up": True, "level": 2})
    
    response = auth_client.post('/sandbox/attack', data={'username': "x"})
    assert response.status_code == 200
    assert b"Level Up" in response.data
