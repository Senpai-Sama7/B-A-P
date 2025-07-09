"""
Main entrypoint for the AI Analytics Platform FastAPI app.
"""
import os
import uvicorn
from fastapi import FastAPI, Request, Response, BackgroundTasks, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse
from prometheus_client import generate_latest
from structlog import get_logger

from src.config import get_settings
from src.api.routes.analytics import router as analytics_router
from src.api.routes.data import router as data_router
from src.api.routes.pipeline import router as pipeline_router
from src.api.middleware.auth import AuthenticationMiddleware
from src.core.database import DatabaseManager
from src.core.cache import CacheManager
from src.utils.logger import setup_logging
from src.utils.metrics import REQUESTS, LATENCY
from src.api.exception_handlers import app_exception_handler, generic_exception_handler, AppException

settings = get_settings()
setup_logging(settings.LOG_LEVEL)
logger = get_logger()

app = FastAPI(
    title="AI Analytics Platform",
    version="1.0.0",
    default_response_class=ORJSONResponse,
    openapi_url="/openapi.json",
)

# Middlewares
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(CORSMiddleware, allow_origins=settings.ALLOWED_ORIGINS, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.add_middleware(AuthenticationMiddleware)

# Routers
app.include_router(analytics_router, prefix="/api/analytics")
app.include_router(data_router, prefix="/api/data")
app.include_router(pipeline_router, prefix="/api/pipeline")

# Register global exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Health, readiness, and metrics endpoints
@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/ready")
async def ready():
    return {"status": "ready"}

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")

if __name__ == "__main__":
    uvicorn.run("src.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
