"""
Performance tests for the AI Analytics Platform.
"""

import pytest
import time
import asyncio
from src.etl.pipeline import run_etl_pipeline, ETLPipeline
from src.models.analytics_models import PipelineRequest


@pytest.mark.asyncio
async def test_etl_performance():
    """Test ETL pipeline performance."""
    request = PipelineRequest(dataset_id="perf-dataset")
    user = "perf-user"
    start = time.time()
    await run_etl_pipeline(request, user)
    elapsed = time.time() - start
    # Pipeline should complete in reasonable time
    assert elapsed < 2.0, f"ETL took too long: {elapsed:.2f}s"


@pytest.mark.asyncio
async def test_concurrent_etl_runs():
    """Test multiple concurrent ETL runs."""
    pipeline = ETLPipeline()

    async def run_job(i):
        request = PipelineRequest(dataset_id=f"concurrent-{i}")
        await pipeline.run(request, user="test-user")

    start = time.time()
    await asyncio.gather(*[run_job(i) for i in range(10)])
    elapsed = time.time() - start

    # 10 concurrent jobs should complete in reasonable time
    assert elapsed < 5.0, f"Concurrent ETL took too long: {elapsed:.2f}s"


@pytest.mark.asyncio
async def test_etl_throughput():
    """Test ETL pipeline throughput."""
    pipeline = ETLPipeline()
    num_jobs = 50

    start = time.time()

    # Process jobs in batches
    batch_size = 10
    for batch_start in range(0, num_jobs, batch_size):
        batch_jobs = []
        for i in range(batch_start, min(batch_start + batch_size, num_jobs)):
            request = PipelineRequest(dataset_id=f"throughput-{i}")
            batch_jobs.append(pipeline.run(request, user="test-user"))
        await asyncio.gather(*batch_jobs)

    elapsed = time.time() - start
    throughput = num_jobs / elapsed

    # Should process at least 5 jobs per second
    assert throughput > 5.0, f"Low throughput: {throughput:.2f} jobs/s"


@pytest.mark.asyncio
async def test_data_transformation_performance():
    """Test data transformation performance with large datasets."""
    pipeline = ETLPipeline()

    # Create a large dataset
    request = PipelineRequest(dataset_id="large-dataset", parameters={"source": "performance-test"})

    start = time.time()
    raw_data = await pipeline.extract_data(request, "perf-user")
    extract_time = time.time() - start

    start = time.time()
    transformed = await pipeline.transform_data(raw_data)
    transform_time = time.time() - start

    # Transformations should be fast
    assert extract_time < 1.0, f"Extraction too slow: {extract_time:.2f}s"
    assert transform_time < 1.0, f"Transformation too slow: {transform_time:.2f}s"
    assert transformed["summary"]["total_records"] == 100
