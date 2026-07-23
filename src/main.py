"""
Main entrypoint for the AI Analytics Platform FastAPI app.
"""

import uvicorn
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from fastapi import FastAPI, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse
from prometheus_client import generate_latest
from sqlalchemy import text
from structlog import get_logger

from src.config import get_settings
from src.api.routes.analytics import router as analytics_router
from src.api.routes.data import router as data_router
from src.api.routes.pipeline import router as pipeline_router
from src.api.middleware.auth import AuthenticationMiddleware
from src.api.middleware.rate_limit import RateLimitMiddleware
from src.api.middleware.security import SecurityHeadersMiddleware
from src.core.database import db_manager
from src.core.cache import cache_manager
from src.utils.logger import setup_logging
from src.api.exception_handlers import (
    app_exception_handler,
    generic_exception_handler,
    AppException,
)

settings = get_settings()
setup_logging(settings.LOG_LEVEL)
logger = get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Handle startup and shutdown events."""
    # Startup
    logger.info("Starting up AI Analytics Platform...")
    try:
        # Initialize database
        await db_manager.create_tables()
        logger.info("Database initialized")

        # Initialize cache
        await cache_manager.connect()
        logger.info("Cache connected")

        logger.info("AI Analytics Platform started successfully")
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down AI Analytics Platform...")
    try:
        await cache_manager.close()
        logger.info("Cache disconnected")

        await db_manager.close()
        logger.info("Database disconnected")

        logger.info("AI Analytics Platform shut down successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


app = FastAPI(
    title="AI Analytics Platform",
    version="1.0.0",
    description="Enterprise-grade, AI-powered business analytics platform",
    default_response_class=ORJSONResponse,
    openapi_url="/openapi.json",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Middlewares (order matters - first added is outermost)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware, requests_per_minute=60)
app.add_middleware(AuthenticationMiddleware)

# Routers
app.include_router(analytics_router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(data_router, prefix="/api/data", tags=["Data"])
app.include_router(pipeline_router, prefix="/api/pipeline", tags=["Pipeline"])

# Register global exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)


# Health, readiness, and metrics endpoints
@app.get("/health", tags=["Health"])
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": "now"}


@app.get("/ready", tags=["Health"])
async def ready() -> dict[str, str]:
    """Readiness check endpoint."""
    try:
        # Check database connection
        async with db_manager.session() as session:
            await session.execute(text("SELECT 1"))

        # Check cache connection
        await cache_manager.exists("health-check")

        return {"status": "ready", "database": "connected", "cache": "connected"}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")


@app.get("/metrics", tags=["Health"])
async def metrics() -> Response:
    """Prometheus metrics endpoint."""
    return Response(generate_latest(), media_type="text/plain")


@app.get("/", tags=["Root"])
async def root() -> dict[str, Any]:
    """Root endpoint with API information."""
    return {
        "name": "AI Analytics Platform",
        "version": "1.0.0",
        "description": "Enterprise-grade, AI-powered business analytics platform",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
    }


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
