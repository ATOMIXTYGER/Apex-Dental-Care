import csv
import io
from datetime import date
from typing import Any

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.billing import Invoice, Payment


class ReportService:
    @staticmethod
    def get_revenue_report(
        db: Session,
        start_date: date | None = None,
        end_date: date | None = None
    ) -> list[dict[str, Any]]:
        query = db.query(Payment)
        if start_date:
            query = query.filter(Payment.payment_date >= start_date)
        if end_date:
            query = query.filter(Payment.payment_date <= end_date)

        payments = query.order_by(desc(Payment.payment_date)).all()
        return [
            {
                "payment_id": p.id,
                "invoice_number": p.invoice.invoice_number if p.invoice else "",
                "patient_name": p.patient.full_name if p.patient else "",
                "amount": float(p.amount),
                "method": p.payment_method,
                "reference": p.transaction_reference or "",
                "date": p.payment_date.strftime('%Y-%m-%d %H:%M')
            }
            for p in payments
        ]

    @staticmethod
    def get_outstanding_report(db: Session) -> list[dict[str, Any]]:
        invoices = db.query(Invoice).filter(
            Invoice.status.in_(["unpaid", "partially_paid"])
        ).order_by(desc(Invoice.balance)).all()

        return [
            {
                "invoice_id": inv.id,
                "invoice_number": inv.invoice_number,
                "patient_name": inv.patient.full_name if inv.patient else "",
                "patient_phone": inv.patient.phone if inv.patient else "",
                "total": float(inv.total),
                "paid": float(inv.paid_amount),
                "balance": float(inv.balance),
                "due_date": inv.due_date.isoformat(),
                "status": inv.status
            }
            for inv in invoices
        ]

    @staticmethod
    def export_csv(headers: list[str], rows: list[list[Any]]) -> str:
        """Render rows to CSV string."""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(headers)
        for r in rows:
            writer.writerow(r)
        return output.getvalue()
