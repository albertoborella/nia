from fastapi import APIRouter, Depends
from sqlmodel import Session, text

from app.database import get_db

router = APIRouter(tags=["health"])


@router.get("/api/v1/health")
def health_check(db: Session = Depends(get_db)):
    checks = {"status": "healthy", "services": {}}

    try:
        db.execute(text("SELECT 1"))
        checks["services"]["database"] = "healthy"
    except Exception:
        checks["services"]["database"] = "unhealthy"
        checks["status"] = "degraded"

    return checks
