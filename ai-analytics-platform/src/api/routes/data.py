"""
Data upload, listing, and retrieval endpoints.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from typing import Any

router = APIRouter()

@router.post("/upload-data")
async def upload_data(file: UploadFile = File(...)) -> dict[str, Any]:
    """Upload a CSV or JSON file for analytics processing."""
    if not file.filename.endswith((".csv", ".json")):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only CSV or JSON files are accepted.")
    # TODO: Add file content validation and secure processing
    return {"filename": file.filename, "status": "uploaded"}
