from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db

router = APIRouter(tags=["Health & Diagnostics"])

@router.get("/health")
def liveness():
    """Liveness probe to verify web application process is running."""
    return {"status": "ok", "service": "dental-api"}

@router.get("/health/ready")
def readiness(db: Session = Depends(get_db)):
    """Readiness probe to verify database connectivity and readiness to serve traffic."""
    try:
        # Execute quick heartbeat query
        db.execute(text("SELECT 1"))
        return {
            "status": "ready",
            "database": "connected",
            "service": "dental-api"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "DATABASE_UNAVAILABLE", "message": "Database ping failed."}
        )
