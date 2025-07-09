import pytest
import asyncio
from ai_analytics_platform.src.etl.pipeline import run_etl_pipeline
from ai_analytics_platform.src.models.analytics_models import PipelineRequest

@pytest.mark.asyncio
async def test_parallel_etl_runs():
    async def worker(dataset_id):
        request = PipelineRequest(dataset_id=dataset_id)
        await run_etl_pipeline(request, user="test-user")
    await asyncio.gather(*(worker(f"ds-{i}") for i in range(5)))
