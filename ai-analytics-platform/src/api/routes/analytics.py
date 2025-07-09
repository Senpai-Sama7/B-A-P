"""
AI-driven insights & forecasts.
"""
from fastapi import APIRouter, Query, HTTPException, status
from ...models.analytics_models import ForecastRequest
from ...ai.forecast_engine import generate_forecast
from typing import Any

router = APIRouter()

@router.get("/summary")
async def analytics_summary(dataset_id: str = Query(..., min_length=1, max_length=128)) -> dict[str, Any]:
    """Return a summary of analytics for a given dataset."""
    if not dataset_id.isalnum():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid dataset_id format.")
    return {"summary": f"Summary for {dataset_id}"}

@router.post("/forecast")
async def analytics_forecast(request: ForecastRequest) -> dict[str, Any]:
    """Return a forecast for the provided data and horizon."""
    if not request.data or request.horizon < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid forecast request.")
    forecast = await generate_forecast(request)
    return {"forecast": forecast.forecast}
