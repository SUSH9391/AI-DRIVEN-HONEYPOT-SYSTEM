def test_environments_page_renders(auth_client, mock_fastapi_client):
    response = auth_client.get('/environments/')
    assert response.status_code == 200
    assert b"Simulation Labs" in response.data
    assert b"SQL Injection Lab" in response.data

def test_locked_env_not_enterable(auth_client, mock_fastapi_client):
    # Setup stats to Level 1
    from unittest.mock import AsyncMock
    mock_fastapi_client.get_user_stats = AsyncMock(return_value={"total_xp": 0, "level": 1})
    
    # Try entering Path Traversal (requires level 3, diff 4)
    response = auth_client.post('/sandbox/create', data={'env_type': 'path_traversal'})
    assert response.status_code == 302
    assert '/environments/' in response.headers['Location']
    # Flash would show "You need a higher level"
