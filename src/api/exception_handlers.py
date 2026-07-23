from fastapi import Request
from fastapi.responses import JSONResponse
from src.utils.logger import get_logger
import traceback

logger = get_logger()


class AppException(Exception):
    """Base class for all custom application exceptions."""

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


async def app_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, AppException):
        return await generic_exception_handler(request, exc)
    logger.error(f"AppException: {exc.message} (status {exc.status_code})")
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(f"Unhandled Exception: {str(exc)}\n{traceback.format_exc()}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
