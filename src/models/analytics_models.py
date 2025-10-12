"""
Pydantic models for API requests and responses.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Any, List, Optional, Dict
from datetime import datetime
from enum import Enum

class JobStatus(str, Enum):
    """ETL job status enum."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class PipelineRequest(BaseModel):
    """Request model for pipeline execution."""
    dataset_id: str = Field(..., min_length=1, max_length=128)
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @field_validator("dataset_id")
    @classmethod
    def validate_dataset_id(cls, v: str) -> str:
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError("dataset_id must contain only alphanumeric characters, hyphens, and underscores")
        return v

class PipelineResponse(BaseModel):
    """Response model for pipeline execution."""
    status: str
    job_id: Optional[str] = None
    details: Optional[str] = None
    started_at: Optional[datetime] = None

class ForecastRequest(BaseModel):
    """Request model for forecasting."""
    data: List[float] = Field(..., min_length=1)
    horizon: int = Field(..., gt=0, le=365)
    model: Optional[str] = Field(default=None)
    confidence_level: Optional[float] = Field(default=0.95, ge=0.0, le=1.0)
    
    @field_validator("data")
    @classmethod
    def validate_data(cls, v: List[float]) -> List[float]:
        if len(v) < 2:
            raise ValueError("At least 2 data points required for forecasting")
        return v

class ForecastResponse(BaseModel):
    """Response model for forecasting."""
    forecast: Any
    confidence_intervals: Optional[Dict[str, List[float]]] = None
    model_info: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class DatasetMetadata(BaseModel):
    """Dataset metadata model."""
    name: str = Field(..., min_length=1, max_length=256)
    description: Optional[str] = None
    source: Optional[str] = None
    tags: Optional[List[str]] = Field(default_factory=list)

class DatasetResponse(BaseModel):
    """Response model for dataset information."""
    dataset_id: str
    name: str
    description: Optional[str] = None
    status: str
    row_count: int
    column_count: int
    file_size: int
    created_at: datetime
    created_by: str

class AnalyticsSummary(BaseModel):
    """Analytics summary response model."""
    dataset_id: str
    total_records: int
    summary_statistics: Dict[str, Any]
    insights: Optional[List[str]] = Field(default_factory=list)
    created_at: datetime

class ErrorResponse(BaseModel):
    """Standard error response model."""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    path: Optional[str] = None
