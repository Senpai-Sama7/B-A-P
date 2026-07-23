"""
AI-driven insights & forecasts.
"""

from fastapi import APIRouter, Query, HTTPException, status
from datetime import datetime
from src.models.analytics_models import ForecastRequest, ForecastResponse, AnalyticsSummary
from src.ai.forecast_engine import generate_forecast
from src.utils.logger import get_logger
from src.utils.metrics import AI_REQUESTS, AI_LATENCY
import time

router = APIRouter()
logger = get_logger()


@router.get("/summary", response_model=AnalyticsSummary)
async def analytics_summary(
    dataset_id: str = Query(
        ..., min_length=1, max_length=128, description="Dataset ID to get summary for"
    )
) -> AnalyticsSummary:
    """Return a summary of analytics for a given dataset."""
    start_time = time.time()

    try:
        # Validate dataset_id format
        if not dataset_id.replace("-", "").replace("_", "").isalnum():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid dataset_id format. Must contain only alphanumeric characters, hyphens, and underscores.",
            )

        # TODO: Fetch real data from database
        summary = AnalyticsSummary(
            dataset_id=dataset_id,
            total_records=1000,
            summary_statistics={
                "mean": 42.5,
                "median": 40.0,
                "std_dev": 12.3,
                "min": 10.0,
                "max": 100.0,
            },
            insights=[
                f"Dataset {dataset_id} contains 1000 records",
                "Data shows normal distribution",
                "No anomalies detected",
            ],
            created_at=datetime.utcnow(),
        )

        AI_REQUESTS.labels(operation="summary", status="success").inc()
        AI_LATENCY.labels(operation="summary").observe(time.time() - start_time)

        logger.info(f"Generated analytics summary for dataset {dataset_id}")
        return summary

    except HTTPException:
        AI_REQUESTS.labels(operation="summary", status="error").inc()
        raise
    except Exception as e:
        AI_REQUESTS.labels(operation="summary", status="error").inc()
        logger.error(f"Failed to generate summary for {dataset_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate analytics summary: {str(e)}",
        )


@router.post("/forecast", response_model=ForecastResponse)
async def analytics_forecast(request: ForecastRequest) -> ForecastResponse:
    """Return a forecast for the provided data and horizon."""
    start_time = time.time()

    try:
        if not request.data or request.horizon < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid forecast request. Data must not be empty and horizon must be positive.",
            )

        # Generate forecast using AI
        forecast = await generate_forecast(request)

        AI_REQUESTS.labels(operation="forecast", status="success").inc()
        AI_LATENCY.labels(operation="forecast").observe(time.time() - start_time)

        logger.info(
            f"Generated forecast for {len(request.data)} data points with horizon {request.horizon}"
        )
        return forecast

    except HTTPException:
        AI_REQUESTS.labels(operation="forecast", status="error").inc()
        raise
    except Exception as e:
        AI_REQUESTS.labels(operation="forecast", status="error").inc()
        logger.error(f"Failed to generate forecast: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate forecast: {str(e)}",
        )
