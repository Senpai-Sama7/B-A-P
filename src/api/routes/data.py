"""
Data upload, listing, and retrieval endpoints.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Query, Depends
from typing import Any, List, Optional
import uuid
from datetime import datetime
from src.utils.logger import get_logger
from src.utils.metrics import REQUESTS, LATENCY
from src.models.analytics_models import DatasetResponse, DatasetMetadata
import time

router = APIRouter()
logger = get_logger()

# Allowed file extensions and max file size
ALLOWED_EXTENSIONS = {".csv", ".json", ".xlsx", ".parquet"}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

@router.post("/upload-data", response_model=DatasetResponse)
async def upload_data(
    file: UploadFile = File(..., description="Data file to upload (CSV, JSON, XLSX, or Parquet)"),
    name: Optional[str] = Query(None, description="Dataset name"),
    description: Optional[str] = Query(None, description="Dataset description"),
) -> DatasetResponse:
    """Upload a CSV, JSON, XLSX, or Parquet file for analytics processing."""
    start_time = time.time()
    
    try:
        # Validate file extension
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename is required"
            )
        
        file_ext = "." + file.filename.split(".")[-1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Only {', '.join(ALLOWED_EXTENSIONS)} files are accepted."
            )
        
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Validate file size
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE / (1024*1024)}MB"
            )
        
        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is empty"
            )
        
        # Generate dataset ID
        dataset_id = f"ds-{uuid.uuid4().hex[:12]}"
        
        # TODO: Process and store file content
        # For now, just log and return metadata
        logger.info(f"Uploaded file {file.filename} with size {file_size} bytes as dataset {dataset_id}")
        
        response = DatasetResponse(
            dataset_id=dataset_id,
            name=name or file.filename,
            description=description,
            status="uploaded",
            row_count=0,  # TODO: Calculate from actual data
            column_count=0,  # TODO: Calculate from actual data
            file_size=file_size,
            created_at=datetime.utcnow(),
            created_by="system",  # TODO: Get from authentication
        )
        
        REQUESTS.labels(method="POST", endpoint="/api/data/upload-data", status="200").inc()
        LATENCY.labels(method="POST", endpoint="/api/data/upload-data").observe(time.time() - start_time)
        
        return response
        
    except HTTPException:
        REQUESTS.labels(method="POST", endpoint="/api/data/upload-data", status=str(status.HTTP_400_BAD_REQUEST)).inc()
        raise
    except Exception as e:
        logger.error(f"Failed to upload file: {e}")
        REQUESTS.labels(method="POST", endpoint="/api/data/upload-data", status="500").inc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )

@router.get("/datasets", response_model=List[DatasetResponse])
async def list_datasets(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
) -> List[DatasetResponse]:
    """List all datasets with pagination."""
    try:
        # TODO: Fetch from database
        datasets: List[DatasetResponse] = []
        
        logger.info(f"Listed {len(datasets)} datasets")
        return datasets
        
    except Exception as e:
        logger.error(f"Failed to list datasets: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list datasets: {str(e)}"
        )

@router.get("/datasets/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(dataset_id: str) -> DatasetResponse:
    """Get details of a specific dataset."""
    try:
        # TODO: Fetch from database
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset {dataset_id} not found"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get dataset {dataset_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dataset: {str(e)}"
        )
