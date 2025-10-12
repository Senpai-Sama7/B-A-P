"""
Trigger ETL & AI pipeline orchestration.
"""
import asyncio
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from typing import Optional
from src.api.middleware.auth import get_current_user_optional
from src.etl.pipeline import run_etl_pipeline
from src.ai.insights_generator import generate_insights
from src.models.analytics_models import PipelineRequest, PipelineResponse
from src.utils.logger import get_logger
from src.utils.metrics import ETL_JOBS, ETL_DURATION
import time

router = APIRouter()
logger = get_logger()

@router.post("/run", response_model=PipelineResponse)
async def run_pipeline(
    request: PipelineRequest,
    background_tasks: BackgroundTasks,
    user: Optional[str] = Depends(get_current_user_optional)
) -> PipelineResponse:
    """Orchestrate ETL and AI analytics pipeline for a given dataset and parameters."""
    job_id = f"job-{uuid.uuid4().hex[:12]}"
    start_time = time.time()
    current_user = user or "anonymous"
    
    try:
        logger.info(f"Starting pipeline for dataset {request.dataset_id} by {current_user}", job_id=job_id)
        
        # Define the background task
        async def etl_and_ai():
            try:
                ETL_JOBS.labels(status="running").inc()
                
                # Run ETL and AI insights in parallel
                await asyncio.gather(
                    run_etl_pipeline(request, current_user),
                    generate_insights(request.dataset_id, current_user)
                )
                
                duration = time.time() - start_time
                ETL_DURATION.observe(duration)
                ETL_JOBS.labels(status="completed").inc()
                
                logger.info(
                    f"Pipeline completed for dataset {request.dataset_id}",
                    job_id=job_id,
                    duration=duration
                )
                
            except Exception as e:
                ETL_JOBS.labels(status="failed").inc()
                logger.error(
                    f"Pipeline failed for dataset {request.dataset_id}",
                    job_id=job_id,
                    error=str(e),
                    exc_info=True
                )
        
        # Add task to background
        background_tasks.add_task(etl_and_ai)
        
        response = PipelineResponse(
            status="started",
            job_id=job_id,
            details="ETL and AI tasks running in background",
            started_at=datetime.utcnow(),
        )
        
        logger.info(f"Pipeline job {job_id} queued successfully")
        return response
        
    except Exception as e:
        ETL_JOBS.labels(status="failed").inc()
        logger.error(f"Failed to start pipeline for dataset {request.dataset_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start pipeline: {str(e)}"
        )

@router.get("/status/{job_id}")
async def get_pipeline_status(job_id: str) -> dict:
    """Get the status of a pipeline job."""
    try:
        # TODO: Implement job status tracking in database
        logger.info(f"Checking status for job {job_id}")
        
        return {
            "job_id": job_id,
            "status": "running",  # TODO: Get from database
            "message": "Job status tracking to be implemented",
        }
        
    except Exception as e:
        logger.error(f"Failed to get status for job {job_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get job status: {str(e)}"
        )
