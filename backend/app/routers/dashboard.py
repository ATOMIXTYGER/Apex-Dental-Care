from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.dashboard import DashboardAnalyticsResponse, DashboardSummaryResponse
from app.security.dependencies import get_current_user
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Clinic Dashboard & Analytics"])

@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(
    period: str = Query("30d", pattern="^(today|7d|30d)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve database-aggregated clinic KPIs and metrics."""
    return DashboardService.get_summary(db, period=period)

@router.get("/analytics", response_model=DashboardAnalyticsResponse)
def get_dashboard_analytics(
    days: int = Query(30, ge=7, le=90),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve chart trend data for appointments, procedures, revenue, and new patients."""
    return DashboardService.get_analytics(db, days=days)
