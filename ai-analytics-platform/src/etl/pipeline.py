import asyncio
from ai_analytics_platform.src.models.analytics_models import PipelineRequest
from ai_analytics_platform.src.core.database import get_db
from ai_analytics_platform.src.core.cache import get_redis
from ai_analytics_platform.src.utils.logger import get_logger
from typing import Any

logger = get_logger()

async def extract_data(request: PipelineRequest, user: str) -> Any:
    """Async extract step (placeholder for real logic)."""
    await asyncio.sleep(0.1)  # Simulate I/O
    logger.info(f"Extracted data for {request.dataset_id} by {user}")
    return {"raw": f"data for {request.dataset_id}"}

async def transform_data(raw_data: Any) -> Any:
    """Async transform step (placeholder for real logic)."""
    await asyncio.sleep(0.1)
    return {"transformed": raw_data["raw"].upper()}

async def load_data(transformed_data: Any, request: PipelineRequest, user: str) -> None:
    """Async load step (placeholder for real logic)."""
    await asyncio.sleep(0.1)
    redis = get_redis()
    redis.set(f"etl:{request.dataset_id}", "completed")
    logger.info(f"Loaded data for {request.dataset_id} by {user}")

async def run_etl_pipeline(request: PipelineRequest, user: str) -> None:
    """Orchestrate the ETL pipeline asynchronously with error handling."""
    try:
        raw = await extract_data(request, user)
        transformed = await transform_data(raw)
        await load_data(transformed, request, user)
        logger.info(f"ETL pipeline completed for {request.dataset_id} by {user}")
    except Exception as e:
        logger.error(f"ETL pipeline failed for {request.dataset_id} by {user}: {e}")
        raise
