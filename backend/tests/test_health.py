import pytest


@pytest.mark.asyncio
async def test_health_check_returns_ok(client):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["database"] == "connected"


@pytest.mark.asyncio
async def test_openapi_docs_are_served(client):
    response = await client.get("/api/openapi.json")
    assert response.status_code == 200
    assert response.json()["info"]["title"] == "PLACER API"
