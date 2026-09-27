from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from decimal import Decimal

class DashboardSummaryResponse(BaseModel):
    total_patients: int
    new_patients_period: int
    today_appointments: int
    upcoming_appointments: int
    pending_treatments: int
    completed_treatments: int
    total_revenue: Decimal
    outstanding_payments: Decimal
    followups_due: int

class StatusCount(BaseModel):
    status: str
    count: int

class ProcedureCount(BaseModel):
    procedure_name: str
    count: int

class RevenueTrendPoint(BaseModel):
    date: str
    revenue: Decimal
    invoiced: Decimal

class PatientTrendPoint(BaseModel):
    date: str
    new_patients: int

class DashboardAnalyticsResponse(BaseModel):
    appointments_by_status: List[StatusCount]
    treatments_by_procedure: List[ProcedureCount]
    revenue_trend: List[RevenueTrendPoint]
    patients_trend: List[PatientTrendPoint]
