from pydantic import BaseModel
from typing import Any, List, Optional

class PipelineRequest(BaseModel):
    dataset_id: str
    parameters: Optional[dict] = None

class PipelineResponse(BaseModel):
    status: str
    details: Optional[str] = None

class ForecastRequest(BaseModel):
    data: List[float]
    horizon: int

class ForecastResponse(BaseModel):
    forecast: Any
