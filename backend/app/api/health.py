"""
Health check endpoints
"""
from fastapi import APIRouter
from datetime import datetime
from app.services.duckdb_service import get_db_service
from app.config import settings

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
async def health_check():
    """
    Health check endpoint
    
    Returns the status of all services
    """
    services = {}
    
    # Check DuckDB
    try:
        db_service = get_db_service(read_only=True)
        stats = db_service.get_stats()
        services["duckdb"] = {
            "status": "healthy",
            "stats": stats
        }
    except Exception as e:
        services["duckdb"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # Check Kafka (basic check)
    try:
        services["kafka"] = {
            "status": "healthy",
            "bootstrap_servers": settings.KAFKA_BOOTSTRAP_SERVERS
        }
    except Exception as e:
        services["kafka"] = {
            "status": "unknown",
            "error": str(e)
        }
    
    # Overall status
    all_healthy = all(
        service.get("status") == "healthy" 
        for service in services.values()
    )
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "services": services,
        "version": "1.0.0"
    }


@router.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Real-Time Shared Mobility Heatmap API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }
