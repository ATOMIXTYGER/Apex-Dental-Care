from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from decimal import Decimal
from app.database import Base

class ProcedureCatalog(Base):
    __tablename__ = "procedure_catalog"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(150), nullable=False)
    category = Column(String(100), nullable=False) # Preventive, Restorative, Endodontics, Periodontics, Prosthodontics, Surgery, Orthodontics, Cosmetic
    default_cost = Column(Numeric(10, 2), nullable=False, default=Decimal('0.00'))
    description = Column(Text, nullable=True)

class TreatmentPlan(Base):
    __tablename__ = "treatment_plans"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="RESTRICT"), nullable=False, index=True)
    dentist_id = Column(Integer, ForeignKey("dentists.id", ondelete="RESTRICT"), nullable=False, index=True)
    title = Column(String(150), nullable=False)
    status = Column(String(50), default="active", nullable=False, index=True) # draft, active, completed, cancelled
    estimated_total = Column(Numeric(10, 2), default=Decimal('0.00'), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    patient = relationship("Patient", back_populates="treatment_plans")
    dentist = relationship("Dentist", back_populates="treatment_plans")
    treatments = relationship("TreatmentItem", back_populates="treatment_plan", cascade="all, delete-orphan")

class TreatmentItem(Base):
    __tablename__ = "treatment_items"

    id = Column(Integer, primary_key=True, index=True)
    treatment_plan_id = Column(Integer, ForeignKey("treatment_plans.id", ondelete="CASCADE"), nullable=False, index=True)
    procedure_name = Column(String(150), nullable=False)
    tooth_number = Column(Integer, nullable=True)
    estimated_cost = Column(Numeric(10, 2), default=Decimal('0.00'), nullable=False)
    actual_cost = Column(Numeric(10, 2), default=Decimal('0.00'), nullable=False)
    status = Column(String(50), default="planned", nullable=False, index=True) # planned, in_progress, completed, cancelled
    visit_id = Column(Integer, ForeignKey("visits.id", ondelete="SET NULL"), nullable=True)
    notes = Column(Text, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    treatment_plan = relationship("TreatmentPlan", back_populates="treatments")
    visit = relationship("Visit", back_populates="treatments")
