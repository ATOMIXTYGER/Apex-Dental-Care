from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class MedicineCatalog(Base):
    __tablename__ = "medicine_catalog"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), unique=True, index=True, nullable=False) # e.g. Amoxicillin 500mg
    generic_name = Column(String(150), nullable=True) # e.g. Amoxicillin
    dosage_form = Column(String(50), default="Tablet", nullable=False) # Tablet, Capsule, Syrup, Mouthwash, Gel
    default_dosage = Column(String(100), nullable=True) # e.g. 500mg
    instructions = Column(Text, nullable=True)

class Prescription(Base):
    __tablename__ = "prescriptions"

    id = Column(Integer, primary_key=True, index=True)
    prescription_number = Column(String(50), unique=True, index=True, nullable=False) # RX-2026-001
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="RESTRICT"), nullable=False, index=True)
    dentist_id = Column(Integer, ForeignKey("dentists.id", ondelete="RESTRICT"), nullable=False, index=True)
    visit_id = Column(Integer, ForeignKey("visits.id", ondelete="SET NULL"), nullable=True, index=True)
    diagnosis_summary = Column(String(255), nullable=True)
    general_instructions = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    patient = relationship("Patient", back_populates="prescriptions")
    dentist = relationship("Dentist", back_populates="prescriptions")
    visit = relationship("Visit", back_populates="prescriptions")
    items = relationship("PrescriptionItem", back_populates="prescription", cascade="all, delete-orphan")

class PrescriptionItem(Base):
    __tablename__ = "prescription_items"

    id = Column(Integer, primary_key=True, index=True)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id", ondelete="CASCADE"), nullable=False, index=True)
    medicine_name = Column(String(150), nullable=False)
    dosage = Column(String(100), nullable=False) # e.g. 500 mg
    frequency = Column(String(100), nullable=False) # e.g. 1-0-1, Three times daily
    duration = Column(String(100), nullable=False) # e.g. 5 days
    timing = Column(String(100), default="After Food", nullable=False) # Before Food, After Food, With Food
    instructions = Column(Text, nullable=True)

    prescription = relationship("Prescription", back_populates="items")
