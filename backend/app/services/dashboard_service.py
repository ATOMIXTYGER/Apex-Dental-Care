from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc

from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.treatment import TreatmentItem
from app.models.billing import Invoice, Payment
from app.models.followup import FollowUp
from app.schemas.dashboard import (
    DashboardSummaryResponse, DashboardAnalyticsResponse,
    StatusCount, ProcedureCount, RevenueTrendPoint, PatientTrendPoint
)

class DashboardService:
    @staticmethod
    def get_summary(db: Session, period: str = "30d") -> DashboardSummaryResponse:
        today = date.today()
        
        # Period start
        if period == "today":
            period_start = datetime.combine(today, datetime.min.time(), tzinfo=timezone.utc)
        elif period == "7d":
            period_start = datetime.combine(today - timedelta(days=7), datetime.min.time(), tzinfo=timezone.utc)
        else: # default 30d
            period_start = datetime.combine(today - timedelta(days=30), datetime.min.time(), tzinfo=timezone.utc)

        # Total active patients
        total_patients = db.query(func.count(Patient.id)).filter(Patient.is_deleted == False).scalar() or 0

        # New patients in period
        new_patients = db.query(func.count(Patient.id)).filter(
            Patient.is_deleted == False,
            Patient.created_at >= period_start
        ).scalar() or 0

        # Today's appointments
        today_appts = db.query(func.count(Appointment.id)).filter(
            Appointment.appointment_date == today,
            Appointment.status.notin_(["cancelled"])
        ).scalar() or 0

        # Upcoming appointments (future days)
        upcoming_appts = db.query(func.count(Appointment.id)).filter(
            Appointment.appointment_date > today,
            Appointment.status.notin_(["cancelled", "completed"])
        ).scalar() or 0

        # Pending treatments
        pending_treatments = db.query(func.count(TreatmentItem.id)).filter(
            TreatmentItem.status.in_(["planned", "in_progress"])
        ).scalar() or 0

        # Completed treatments
        completed_treatments = db.query(func.count(TreatmentItem.id)).filter(
            TreatmentItem.status == "completed"
        ).scalar() or 0

        # Total revenue collected
        revenue_sum = db.query(func.sum(Payment.amount)).scalar() or Decimal('0.00')

        # Outstanding balance across all active invoices
        outstanding_sum = db.query(func.sum(Invoice.balance)).filter(
            Invoice.status.in_(["unpaid", "partially_paid"])
        ).scalar() or Decimal('0.00')

        # Follow-ups due (pending up to today)
        followups_due = db.query(func.count(FollowUp.id)).filter(
            FollowUp.status == "pending",
            FollowUp.scheduled_date <= today
        ).scalar() or 0

        return DashboardSummaryResponse(
            total_patients=total_patients,
            new_patients_period=new_patients,
            today_appointments=today_appts,
            upcoming_appointments=upcoming_appts,
            pending_treatments=pending_treatments,
            completed_treatments=completed_treatments,
            total_revenue=Decimal(str(revenue_sum)),
            outstanding_payments=Decimal(str(outstanding_sum)),
            followups_due=followups_due
        )

    @staticmethod
    def get_analytics(db: Session, days: int = 30) -> DashboardAnalyticsResponse:
        today = date.today()
        start_date = today - timedelta(days=days)

        # 1. Appointments by status
        appt_stats = db.query(
            Appointment.status,
            func.count(Appointment.id)
        ).group_by(Appointment.status).all()

        appointments_by_status = [
            StatusCount(status=status_name, count=count) for status_name, count in appt_stats
        ]

        # 2. Treatments by procedure
        treatment_stats = db.query(
            TreatmentItem.procedure_name,
            func.count(TreatmentItem.id)
        ).group_by(TreatmentItem.procedure_name).order_by(desc(func.count(TreatmentItem.id))).limit(8).all()

        treatments_by_procedure = [
            ProcedureCount(procedure_name=proc, count=cnt) for proc, cnt in treatment_stats
        ]

        # 3. Revenue trend over last N days
        revenue_points = []
        for d in range(min(days, 14)): # 14 daily buckets
            day_target = today - timedelta(days=min(days, 14) - 1 - d)
            next_day = day_target + timedelta(days=1)
            
            day_rev = db.query(func.sum(Payment.amount)).filter(
                Payment.payment_date >= datetime.combine(day_target, datetime.min.time(), tzinfo=timezone.utc),
                Payment.payment_date < datetime.combine(next_day, datetime.min.time(), tzinfo=timezone.utc)
            ).scalar() or Decimal('0.00')

            day_inv = db.query(func.sum(Invoice.total)).filter(
                Invoice.issue_date == day_target
            ).scalar() or Decimal('0.00')

            revenue_points.append(RevenueTrendPoint(
                date=day_target.strftime('%b %d'),
                revenue=Decimal(str(day_rev)),
                invoiced=Decimal(str(day_inv))
            ))

        # 4. Patients registration trend
        patient_points = []
        for d in range(min(days, 14)):
            day_target = today - timedelta(days=min(days, 14) - 1 - d)
            next_day = day_target + timedelta(days=1)

            count = db.query(func.count(Patient.id)).filter(
                Patient.created_at >= datetime.combine(day_target, datetime.min.time(), tzinfo=timezone.utc),
                Patient.created_at < datetime.combine(next_day, datetime.min.time(), tzinfo=timezone.utc),
                Patient.is_deleted == False
            ).scalar() or 0

            patient_points.append(PatientTrendPoint(
                date=day_target.strftime('%b %d'),
                new_patients=count
            ))

        return DashboardAnalyticsResponse(
            appointments_by_status=appointments_by_status,
            treatments_by_procedure=treatments_by_procedure,
            revenue_trend=revenue_points,
            patients_trend=patient_points
        )
