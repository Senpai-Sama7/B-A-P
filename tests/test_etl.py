import pytest
import pytest_asyncio
from src.etl.pipeline import run_etl_pipeline
from src.models.analytics_models import PipelineRequest

@pytest.mark.asyncio
async def test_run_etl_pipeline():
    request = PipelineRequest(dataset_id="test-dataset")
    user = "test-user"
    await run_etl_pipeline(request, user)
    # No assertion: just ensure no exceptions for now
