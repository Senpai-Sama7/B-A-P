import pytest
import time
import asyncio
from ai_analytics_platform.src.etl.pipeline import run_etl_pipeline
from ai_analytics_platform.src.models.analytics_models import PipelineRequest

@pytest.mark.asyncio
async def test_etl_performance():
    request = PipelineRequest(dataset_id="perf-dataset")
    user = "perf-user"
    start = time.time()
    await run_etl_pipeline(request, user)
    elapsed = time.time() - start
    assert elapsed < 2  # Example threshold
