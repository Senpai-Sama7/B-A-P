"""
ETL pipeline tests.
"""

import pytest
from src.etl.pipeline import run_etl_pipeline, ETLPipeline
from src.models.analytics_models import PipelineRequest
from src.core.cache import cache_manager


@pytest.mark.asyncio
async def test_run_etl_pipeline():
    """Test basic ETL pipeline execution."""
    request = PipelineRequest(dataset_id="test-dataset")
    user = "test-user"

    await run_etl_pipeline(request, user)

    # Verify pipeline completed successfully
    cache = await cache_manager.connect()
    status = await cache.get(f"etl:status:{request.dataset_id}")
    assert status == "completed"


@pytest.mark.asyncio
async def test_etl_extract_stage():
    """Test data extraction stage."""
    pipeline = ETLPipeline()
    request = PipelineRequest(dataset_id="extract-test")

    raw_data = await pipeline.extract_data(request, user="test-user")

    assert raw_data is not None
    assert "dataset_id" in raw_data
    assert "records" in raw_data
    assert "metadata" in raw_data
    assert len(raw_data["records"]) > 0


@pytest.mark.asyncio
async def test_etl_transform_stage():
    """Test data transformation stage."""
    pipeline = ETLPipeline()

    # Create sample raw data
    raw_data = {
        "dataset_id": "transform-test",
        "records": [
            {"id": 1, "value": 10, "category": "A"},
            {"id": 2, "value": 20, "category": "B"},
            {"id": 3, "value": 30, "category": "A"},
        ],
        "metadata": {},
    }

    transformed = await pipeline.transform_data(raw_data)

    assert transformed is not None
    assert "summary" in transformed
    assert "records" in transformed
    assert transformed["summary"]["total_records"] == 3
    assert "mean_value" in transformed["summary"]


@pytest.mark.asyncio
async def test_etl_load_stage():
    """Test data loading stage."""
    pipeline = ETLPipeline()
    request = PipelineRequest(dataset_id="load-test")

    transformed_data = {
        "dataset_id": "load-test",
        "records": [{"id": 1, "value": 100}],
        "summary": {"total_records": 1},
        "metadata": {},
    }

    await pipeline.load_data(transformed_data, request, user="test-user")

    # Verify data was loaded to cache
    cache = await cache_manager.connect()
    status = await cache.get(f"etl:status:{request.dataset_id}")
    assert status == "completed"


@pytest.mark.asyncio
async def test_etl_pipeline_with_parameters():
    """Test ETL pipeline with custom parameters."""
    request = PipelineRequest(
        dataset_id="params-test", parameters={"source": "test-source", "batch_size": 100}
    )

    await run_etl_pipeline(request, user="test-user")

    # Should complete successfully even with parameters
    cache = await cache_manager.connect()
    status = await cache.get(f"etl:status:{request.dataset_id}")
    assert status == "completed"


@pytest.mark.asyncio
async def test_etl_pipeline_error_handling():
    """Test ETL pipeline error handling."""
    pipeline = ETLPipeline()

    # Test with invalid data that should cause transformation to fail
    raw_data = {
        "dataset_id": "error-test",
        "records": None,  # This will cause an error
        "metadata": {},
    }

    with pytest.raises(Exception):
        await pipeline.transform_data(raw_data)
