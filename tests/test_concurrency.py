"""
Concurrency tests for the AI Analytics Platform.
"""
import pytest
import asyncio
from src.etl.pipeline import run_etl_pipeline, ETLPipeline
from src.models.analytics_models import PipelineRequest
from src.core.cache import cache_manager

@pytest.mark.asyncio
async def test_parallel_etl_runs():
    """Test multiple ETL pipelines running in parallel."""
    async def worker(dataset_id):
        request = PipelineRequest(dataset_id=dataset_id)
        await run_etl_pipeline(request, user="test-user")
    
    # Run 5 pipelines in parallel
    await asyncio.gather(*(worker(f"ds-{i}") for i in range(5)))
    
    # Verify all completed
    cache = await cache_manager.connect()
    for i in range(5):
        status = await cache.get(f"etl:status:ds-{i}")
        assert status == "completed"

@pytest.mark.asyncio
async def test_concurrent_cache_operations():
    """Test concurrent cache operations."""
    cache = await cache_manager.connect()
    
    async def write_and_read(key, value):
        await cache.set(key, value)
        result = await cache.get(key)
        assert result == value
    
    # Run multiple concurrent cache operations
    tasks = [write_and_read(f"key-{i}", f"value-{i}") for i in range(10)]
    await asyncio.gather(*tasks)

@pytest.mark.asyncio
async def test_race_condition_handling():
    """Test that concurrent operations don't cause race conditions."""
    pipeline = ETLPipeline()
    dataset_id = "race-test"
    
    async def run_pipeline():
        request = PipelineRequest(dataset_id=dataset_id)
        await pipeline.run(request, user="test-user")
    
    # Run the same pipeline multiple times concurrently
    await asyncio.gather(*[run_pipeline() for _ in range(3)])
    
    # Should complete without errors
    cache = await cache_manager.connect()
    status = await cache.get(f"etl:status:{dataset_id}")
    assert status == "completed"

@pytest.mark.asyncio
async def test_concurrent_data_transformations():
    """Test concurrent data transformations."""
    pipeline = ETLPipeline()
    
    async def transform_data(i):
        raw_data = {
            "dataset_id": f"transform-{i}",
            "records": [{"id": j, "value": j * 10} for j in range(100)],
            "metadata": {},
        }
        result = await pipeline.transform_data(raw_data)
        assert result is not None
        assert result["summary"]["total_records"] == 100
    
    # Transform multiple datasets concurrently
    await asyncio.gather(*[transform_data(i) for i in range(5)])

@pytest.mark.asyncio
async def test_asyncio_semaphore_limiting():
    """Test that we can limit concurrent operations."""
    semaphore = asyncio.Semaphore(3)  # Max 3 concurrent operations
    counter = {"current": 0, "max": 0}
    
    async def limited_operation(i):
        async with semaphore:
            counter["current"] += 1
            counter["max"] = max(counter["max"], counter["current"])
            await asyncio.sleep(0.1)
            counter["current"] -= 1
    
    # Try to run 10 operations, but only 3 should run concurrently
    await asyncio.gather(*[limited_operation(i) for i in range(10)])
    
    # Max concurrent should not exceed semaphore limit
    assert counter["max"] <= 3
