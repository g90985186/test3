from fastapi import FastAPI, Request
from prometheus_client import Counter, Histogram, generate_latest
import time
from typing import Callable
import logging

logger = logging.getLogger(__name__)

# Metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

AI_PROCESSING_TIME = Histogram(
    'ai_processing_duration_seconds',
    'AI model processing time',
    ['model_name']
)

class MonitoringMiddleware:
    def __init__(self, app: FastAPI):
        self.app = app

    async def __call__(self, request: Request, call_next: Callable):
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Record metrics
        duration = time.time() - start_time
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        REQUEST_LATENCY.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)
        
        return response

def setup_monitoring(app: FastAPI):
    """Setup monitoring for the application."""
    # Add monitoring middleware
    app.add_middleware(MonitoringMiddleware)
    
    # Add metrics endpoint
    @app.get("/metrics")
    async def metrics():
        return Response(generate_latest(), media_type="text/plain")
    
    # Enhanced health check
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "version": "1.0.0",
            "components": {
                "database": check_database_health(),
                "ai_models": check_ai_models_health(),
                "cache": check_cache_health()
            }
        }

def check_database_health() -> dict:
    """Check database health."""
    try:
        # Add actual database health check
        return {"status": "healthy"}
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return {"status": "unhealthy", "error": str(e)}

def check_ai_models_health() -> dict:
    """Check AI models health."""
    try:
        # Add actual AI models health check
        return {"status": "healthy"}
    except Exception as e:
        logger.error(f"AI models health check failed: {str(e)}")
        return {"status": "unhealthy", "error": str(e)}

def check_cache_health() -> dict:
    """Check cache health."""
    try:
        # Add actual cache health check
        return {"status": "healthy"}
    except Exception as e:
        logger.error(f"Cache health check failed: {str(e)}")
        return {"status": "unhealthy", "error": str(e)} 