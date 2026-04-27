def test_dashboard_requires_auth(client):
    response = client.get('/dashboard/')
    assert response.status_code == 302
    assert '/auth/login' in response.headers['Location']

def test_dashboard_renders_stats(auth_client, mock_fastapi_client):
    response = auth_client.get('/dashboard/')
    assert response.status_code == 200
    assert b"Welcome back, testuser" in response.data
    mock_fastapi_client.get_user_stats.assert_called_once_with("u-123", jwt="fake-jwt-token")
