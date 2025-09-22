"""
Health check endpoints for olKAN v2.0
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from datetime import datetime
from app.api.deps import (
    check_database_health,
    check_weaviate_health,
    check_ai_services_health,
    get_weaviate_client
)
from app.core.config import settings

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "service": "olKAN"
    }


@router.get("/detailed")
async def detailed_health_check(
    db_healthy: bool = Depends(check_database_health),
    weaviate_healthy: bool = Depends(check_weaviate_health),
    ai_services_healthy: Dict[str, bool] = Depends(check_ai_services_health)
) -> Dict[str, Any]:
    """Detailed health check with component status"""
    
    components = {
        "database": {
            "status": "healthy" if db_healthy else "unhealthy",
            "type": "sqlite" if "sqlite" in settings.database_url else "postgresql"
        },
        "weaviate": {
            "status": "healthy" if weaviate_healthy else "unhealthy",
            "url": settings.weaviate_url
        },
        "ai_services": {
            "vector_search": "healthy" if ai_services_healthy.get("vector_search") else "unhealthy",
            "knowledge_graph": "healthy" if ai_services_healthy.get("knowledge_graph") else "unhealthy",
            "quality_assessment": "healthy" if ai_services_healthy.get("quality_assessment") else "unhealthy",
            "agents": "healthy" if ai_services_healthy.get("agents") else "unhealthy"
        }
    }
    
    # Determine overall status
    all_healthy = all([
        db_healthy,
        weaviate_healthy,
        all(ai_services_healthy.values())
    ])
    
    overall_status = "healthy" if all_healthy else "degraded"
    
    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "service": "olKAN",
        "components": components
    }


@router.get("/weaviate")
async def weaviate_health_check(
    weaviate_client = Depends(get_weaviate_client)
) -> Dict[str, Any]:
    """Detailed Weaviate health check"""
    try:
        health_info = await weaviate_client.health_check()
        return health_info
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Weaviate health check failed: {str(e)}")


@router.get("/ready")
async def readiness_check(
    db_healthy: bool = Depends(check_database_health),
    weaviate_healthy: bool = Depends(check_weaviate_health)
) -> Dict[str, Any]:
    """Readiness check for Kubernetes"""
    
    if not db_healthy:
        raise HTTPException(status_code=503, detail="Database not ready")
    
    if not weaviate_healthy:
        raise HTTPException(status_code=503, detail="Weaviate not ready")
    
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/live")
async def liveness_check() -> Dict[str, Any]:
    """Liveness check for Kubernetes"""
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }
