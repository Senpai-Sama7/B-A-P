"""
Authentication middleware and dependencies.
"""
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional
from src.core.security import verify_token
from src.utils.logger import get_logger

logger = get_logger()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token", auto_error=False)
security = HTTPBearer(auto_error=False)

# Public paths that don't require authentication
PUBLIC_PATHS = [
    "/health",
    "/ready",
    "/metrics",
    "/docs",
    "/openapi.json",
    "/redoc",
]

class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Middleware for handling authentication on protected routes."""
    
    async def dispatch(self, request: Request, call_next):
        """Process the request and verify authentication."""
        # Skip auth for public paths
        if any(request.url.path.startswith(path) for path in PUBLIC_PATHS):
            return await call_next(request)
        
        # For now, just pass through - can be enhanced later
        # In production, you'd verify tokens here
        response = await call_next(request)
        return response

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> str:
    """Get the current user from JWT token."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    user = verify_token(token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[str]:
    """Get the current user from JWT token, returns None if not authenticated."""
    if not credentials:
        return None
    
    token = credentials.credentials
    return verify_token(token)
