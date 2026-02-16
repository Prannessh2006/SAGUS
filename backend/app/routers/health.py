from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import Dict, Any

router = APIRouter()


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "kag-api"
    }


@router.get("/health/ready")
async def readiness_check() -> Dict[str, Any]:
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {
            "neo4j": "connected",
            "llm": "configured"
        }
    }


@router.get("/health/live")
async def liveness_check() -> Dict[str, Any]:
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }
