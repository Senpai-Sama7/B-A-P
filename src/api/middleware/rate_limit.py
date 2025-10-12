"""
Rate limiting middleware for API protection.
"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Tuple
import time
from src.utils.logger import get_logger

logger = get_logger()

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using token bucket algorithm.
    """
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.bucket_capacity = requests_per_minute
        self.refill_rate = requests_per_minute / 60.0  # tokens per second
        self.buckets: Dict[str, Tuple[float, float]] = {}  # ip -> (tokens, last_refill)
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    def _refill_bucket(self, ip: str) -> float:
        """Refill the token bucket for a given IP."""
        now = time.time()
        
        if ip not in self.buckets:
            self.buckets[ip] = (self.bucket_capacity, now)
            return self.bucket_capacity
        
        tokens, last_refill = self.buckets[ip]
        
        # Calculate tokens to add based on time elapsed
        time_passed = now - last_refill
        tokens_to_add = time_passed * self.refill_rate
        
        # Update bucket
        new_tokens = min(self.bucket_capacity, tokens + tokens_to_add)
        self.buckets[ip] = (new_tokens, now)
        
        return new_tokens
    
    async def dispatch(self, request: Request, call_next):
        """Process the request with rate limiting."""
        # Skip rate limiting for health check endpoints
        if request.url.path in ["/health", "/ready", "/metrics"]:
            return await call_next(request)
        
        ip = self._get_client_ip(request)
        
        # Refill bucket and check if request is allowed
        tokens = self._refill_bucket(ip)
        
        if tokens < 1:
            logger.warning(f"Rate limit exceeded for IP {ip}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later.",
                headers={"Retry-After": "60"}
            )
        
        # Consume one token
        self.buckets[ip] = (tokens - 1, self.buckets[ip][1])
        
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(int(tokens - 1))
        response.headers["X-RateLimit-Reset"] = str(int(time.time() + 60))
        
        return response
