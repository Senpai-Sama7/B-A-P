"""
Prometheus metrics for monitoring the application.
"""
from prometheus_client import Counter, Histogram, Gauge
import time

# Request metrics
REQUESTS = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

# Latency metrics
LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

# Database connection pool metrics
DB_CONNECTIONS = Gauge(
    'db_connections_active',
    'Active database connections'
)

# Cache hit/miss metrics
CACHE_HITS = Counter(
    'cache_hits_total',
    'Total cache hits'
)

CACHE_MISSES = Counter(
    'cache_misses_total',
    'Total cache misses'
)

# ETL pipeline metrics
ETL_JOBS = Counter(
    'etl_jobs_total',
    'Total ETL jobs',
    ['status']
)

ETL_DURATION = Histogram(
    'etl_job_duration_seconds',
    'ETL job duration'
)

# AI operations metrics
AI_REQUESTS = Counter(
    'ai_requests_total',
    'Total AI requests',
    ['operation', 'status']
)

AI_LATENCY = Histogram(
    'ai_request_duration_seconds',
    'AI request latency',
    ['operation']
)

class Metrics:
    """Legacy metrics class for compatibility."""
    def __init__(self):
        self.metrics = {}

    def record(self, name: str, value: float):
        self.metrics[name] = value

    def get(self, name: str):
        return self.metrics.get(name)

metrics = Metrics()
