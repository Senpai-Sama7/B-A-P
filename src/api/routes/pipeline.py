"""
Trigger ETL & show status (naïve demo impl).
"""
import asyncio
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from ..middleware.auth import get_current_user
from ...etl.pipeline import run_etl_pipeline
from ...ai.insights_generator import generate_insights
from ...models.analytics_models import PipelineRequest, PipelineResponse
from ...utils.logger import get_logger

router = APIRouter()
logger = get_logger()

@router.post("/run", response_model=PipelineResponse)
async def run_pipeline(
    request: PipelineRequest,
    background_tasks: BackgroundTasks,
    user=Depends(get_current_user)
) -> PipelineResponse:
    """Orchestrate ETL and AI analytics pipeline for a given dataset and parameters."""
    try:
        # Run ETL and AI insights in parallel as background tasks
        async def etl_and_ai():
            await asyncio.gather(
                run_etl_pipeline(request, user),
                generate_insights(request.dataset_id, user)
            )
        background_tasks.add_task(asyncio.create_task, etl_and_ai())
        logger.info(f"Pipeline started for dataset {request.dataset_id} by {user}")
        return PipelineResponse(status="Pipeline started", details="ETL and AI tasks running in background.")
    except Exception as e:
        logger.error(f"Pipeline failed for dataset {request.dataset_id} by {user}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
