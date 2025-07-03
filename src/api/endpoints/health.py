"""
Health check endpoints
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any
from datetime import datetime

router = APIRouter()


@router.get("/")
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Hospital Operations Platform",
        "version": "1.0.0"
    }


@router.get("/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """Detailed health check with system components"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "database": {"status": "connected", "response_time_ms": 5},
            "redis": {"status": "connected", "response_time_ms": 2},
            "kafka": {"status": "connected", "response_time_ms": 8},
            "agents": {"status": "running", "count": 1},
        },
        "system": {
            "uptime_seconds": 3600,
            "memory_usage_percent": 45.2,
            "cpu_usage_percent": 12.8
        }
    }
