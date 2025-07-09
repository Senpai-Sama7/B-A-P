import pytest
import pytest_asyncio
from httpx import AsyncClient
from ai_analytics_platform.src.main import app

@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_analytics_summary(async_client):
    response = await async_client.get("/api/analytics/summary?dataset_id=test123")
    assert response.status_code == 200
    assert "summary" in response.json()

@pytest.mark.asyncio
async def test_analytics_forecast(async_client):
    payload = {"data": [1, 2, 3], "horizon": 2}
    response = await async_client.post("/api/analytics/forecast", json=payload)
    assert response.status_code == 200
    assert "forecast" in response.json()
