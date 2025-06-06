from fastapi import APIRouter, HTTPException, Depends, Response
from typing import Dict, Any, List
from pydantic import BaseModel
from datetime import datetime, timedelta
import psutil
import sys
import os
from app.core.security import get_auth_dependency, get_admin_dependency
from app.services.ai_service import ai_service
from app.services.ollama_service import OllamaService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class SystemMetrics(BaseModel):
    """System metrics model."""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    uptime: str
    python_version: str
    
class ServiceStatus(BaseModel):
    """Service status model."""
    name: str
    status: str
    last_check: str
    details: Dict[str, Any]

class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: str
    version: str
    services: List[ServiceStatus]
    system: SystemMetrics

@router.get("/health", response_model=HealthResponse)
async def detailed_health_check(auth: str = Depends(get_auth_dependency())):
    """Comprehensive health check endpoint."""
    try:
        # Check system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        uptime = datetime.now() - datetime.fromtimestamp(psutil.boot_time())
        
        system_metrics = SystemMetrics(
            cpu_usage=cpu_percent,
            memory_usage=memory.percent,
            disk_usage=disk.percent,
            uptime=str(uptime),
            python_version=sys.version
        )
        
        # Check services
        services = []
        
        # AI Service status
        try:
            ai_status = {"status": "running", "ollama_available": False}
            services.append(ServiceStatus(
                name="AI Service",
                status="degraded",
                last_check=datetime.now().isoformat(),
                details=ai_status
            ))
        except Exception as e:
            services.append(ServiceStatus(
                name="AI Service",
                status="unhealthy",
                last_check=datetime.now().isoformat(),
                details={"error": str(e)}
            ))
        
        # Database status (basic check)
        try:
            from app.database import engine
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            db_status = "healthy"
            db_details = {"connection": "active"}
        except Exception as e:
            db_status = "unhealthy"
            db_details = {"error": str(e)}
        
        services.append(ServiceStatus(
            name="Database",
            status=db_status,
            last_check=datetime.now().isoformat(),
            details=db_details
        ))
        
        # Overall status
        overall_status = "healthy"
        if any(s.status == "unhealthy" for s in services):
            overall_status = "unhealthy"
        elif any(s.status == "degraded" for s in services):
            overall_status = "degraded"
        
        return HealthResponse(
            status=overall_status,
            timestamp=datetime.now().isoformat(),
            version="1.0.0",
            services=services,
            system=system_metrics
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.get("/metrics")
async def get_metrics(auth: str = Depends(get_auth_dependency())):
    """Get application metrics in Prometheus format."""
    try:
        from prometheus_client import generate_latest
        return Response(generate_latest(), media_type="text/plain")
    except ImportError:
        # Fallback to basic metrics if prometheus_client not available
        return {
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "cpu_usage": psutil.cpu_percent(),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent
            }
        }

@router.get("/status")
async def get_status(auth: str = Depends(get_auth_dependency())):
    """Get basic application status."""
    return {
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@router.get("/logs")
async def get_recent_logs(
    lines: int = 100,
    level: str = "INFO",
    auth: str = Depends(get_admin_dependency())
):
    """Get recent application logs."""
    try:
        # This is a simplified implementation
        # In production, you'd integrate with your logging system
        return {
            "message": "Log retrieval not implemented",
            "note": "Integrate with your logging infrastructure"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving logs: {str(e)}")

@router.post("/restart")
async def restart_service(
    service: str,
    auth: str = Depends(get_admin_dependency())
):
    """Restart a specific service."""
    try:
        if service == "ai":
            await ai_service.initialize()
            return {"message": f"Service {service} restarted successfully"}
        else:
            raise HTTPException(status_code=400, detail=f"Unknown service: {service}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error restarting service: {str(e)}")

@router.get("/performance")
async def get_performance_metrics(auth: str = Depends(get_auth_dependency())):
    """Get detailed performance metrics."""
    try:
        import gc
        import threading
        
        return {
            "timestamp": datetime.now().isoformat(),
            "python": {
                "version": sys.version,
                "gc_counts": gc.get_count(),
                "thread_count": threading.active_count()
            },
            "system": {
                "cpu_count": psutil.cpu_count(),
                "cpu_freq": psutil.cpu_freq()._asdict(),
                "memory": psutil.virtual_memory()._asdict(),
                "disk": psutil.disk_usage('/')._asdict(),
                "network": psutil.net_io_counters()._asdict()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting performance metrics: {str(e)}") 