"""
API endpoint tests.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient
from src.main import app

@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_health_endpoint(async_client):
    """Test health check endpoint."""
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

@pytest.mark.asyncio
async def test_root_endpoint(async_client):
    """Test root endpoint."""
    response = await async_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data

@pytest.mark.asyncio
async def test_analytics_summary(async_client):
    """Test analytics summary endpoint."""
    response = await async_client.get("/api/analytics/summary?dataset_id=test123")
    assert response.status_code == 200
    data = response.json()
    assert "dataset_id" in data
    assert data["dataset_id"] == "test123"

@pytest.mark.asyncio
async def test_analytics_summary_invalid_id(async_client):
    """Test analytics summary with invalid dataset ID."""
    response = await async_client.get("/api/analytics/summary?dataset_id=test@123")
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_analytics_forecast(async_client):
    """Test analytics forecast endpoint."""
    payload = {"data": [1.0, 2.0, 3.0], "horizon": 2}
    response = await async_client.post("/api/analytics/forecast", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "forecast" in data

@pytest.mark.asyncio
async def test_analytics_forecast_invalid_data(async_client):
    """Test forecast with invalid data."""
    payload = {"data": [], "horizon": 2}
    response = await async_client.post("/api/analytics/forecast", json=payload)
    assert response.status_code == 422  # Validation error

@pytest.mark.asyncio
async def test_data_upload_endpoint(async_client):
    """Test data upload endpoint."""
    files = {"file": ("test.csv", b"id,value\n1,100\n2,200", "text/csv")}
    response = await async_client.post("/api/data/upload-data", files=files)
    assert response.status_code == 200
    data = response.json()
    assert "dataset_id" in data
    assert data["status"] == "uploaded"

@pytest.mark.asyncio
async def test_data_upload_invalid_extension(async_client):
    """Test upload with invalid file extension."""
    files = {"file": ("test.txt", b"some text", "text/plain")}
    response = await async_client.post("/api/data/upload-data", files=files)
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_list_datasets(async_client):
    """Test list datasets endpoint."""
    response = await async_client.get("/api/data/datasets")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

@pytest.mark.asyncio
async def test_metrics_endpoint(async_client):
    """Test Prometheus metrics endpoint."""
    response = await async_client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]

@pytest.mark.asyncio
async def test_openapi_docs(async_client):
    """Test OpenAPI documentation endpoint."""
    response = await async_client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "info" in data
    assert "paths" in data
