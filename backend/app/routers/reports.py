from datetime import date

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.security.dependencies import require_roles
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["Reports & Exports"])

@router.get("/revenue")
def get_revenue_report(
    start_date: date | None = None,
    end_date: date | None = None,
    current_user: User = Depends(require_roles("admin", "receptionist")),
    db: Session = Depends(get_db)
):
    """Retrieve detailed payment and revenue report with date range filters."""
    return ReportService.get_revenue_report(db, start_date=start_date, end_date=end_date)

@router.get("/outstanding")
def get_outstanding_report(
    current_user: User = Depends(require_roles("admin", "receptionist")),
    db: Session = Depends(get_db)
):
    """Retrieve all pending and partially paid invoices."""
    return ReportService.get_outstanding_report(db)

@router.get("/revenue/export-csv")
def export_revenue_csv(
    start_date: date | None = None,
    end_date: date | None = None,
    current_user: User = Depends(require_roles("admin", "receptionist")),
    db: Session = Depends(get_db)
):
    """Export revenue report to standard CSV."""
    data = ReportService.get_revenue_report(db, start_date=start_date, end_date=end_date)
    headers = ["Payment ID", "Invoice #", "Patient Name", "Amount (₹)", "Method", "Reference", "Date"]
    rows = [
        [d["payment_id"], d["invoice_number"], d["patient_name"], d["amount"], d["method"], d["reference"], d["date"]]
        for d in data
    ]
    csv_content = ReportService.export_csv(headers, rows)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="revenue_report.csv"'}
    )
