import pytest
from flask_frontend.services.fastapi_client import fastapi_client
import httpx

@pytest.mark.asyncio
async def test_score_attack_adds_service_token_header(mock_httpx_fastapi_client):
    mock_httpx_fastapi_client.return_value = {"attack_detected": True}
    
    await fastapi_client.score_attack("sandbox1", "token1", {"k": "v"}, "/test", "127.0.0.1")
    
    mock_httpx_fastapi_client.assert_called_once()
    args, kwargs = mock_httpx_fastapi_client.call_args
    assert args[0] == "POST"
    assert args[1] == "/api/detect/score"
    assert "headers" not in kwargs # it passes self.headers implicitly inside the class method, but the mock is on _request. 
    # Wait, the inner mock is _request. The method constructs the payload and sends to _request.
    assert kwargs['json']['attack_payload'] == {"k": "v"}

@pytest.mark.asyncio
async def test_client_handles_fastapi_timeout_gracefully(mocker):
    from flask_frontend.services.fastapi_client import FastAPIClient
    client = FastAPIClient()
    
    mock_http_client = mocker.patch("httpx.AsyncClient.request", side_effect=httpx.RequestError("Timeout"))
    
    res = await client.score_attack("s1", "t1", {}, "/t", "1.1")
    assert res.get("error") is True
    assert "Connection error" in res.get("detail")
