"""Health and readiness endpoints for monitoring and orchestration."""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.base import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Liveness probe — returns 200 as long as the service is running.

    Includes a database connectivity check to surface dependency failures.
    """
    health = {
        "status": "ok",
        "version": "0.1.0",
    }
    try:
        db.execute(text("SELECT 1"))
        health["database"] = "connected"
    except Exception as e:  # noqa: BLE001
        health["database"] = f"error: {e}"
        health["status"] = "degraded"
    return health


@router.get("/ready")
def readiness_check(db: Session = Depends(get_db)):
    """Readiness probe — returns 200 only when the service can serve traffic.

    Orchestrators (Kubernetes, Nomad) use this to decide when to route
    traffic to a pod.
    """
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as e:  # noqa: BLE001
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database unavailable: {e}",
        )
