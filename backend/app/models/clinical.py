from datetime import datetime, UTC

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Visit(Base):
    __tablename__ = "visits"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="RESTRICT"), nullable=False, index=True)
    dentist_id = Column(Integer, ForeignKey("dentists.id", ondelete="RESTRICT"), nullable=False, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id", ondelete="SET NULL"), nullable=True, unique=True)
    visit_date = Column(Date, nullable=False, index=True)

    # Clinical examination & vitals
    vitals_blood_pressure = Column(String(50), nullable=True) # e.g. 120/80
    vitals_pulse = Column(Integer, nullable=True)
    chief_complaint = Column(Text, nullable=True)
    oral_findings = Column(Text, nullable=True)
    gum_condition = Column(String(100), nullable=True) # Healthy, Gingivitis, Periodontitis, Bleeding on probing
    hygiene_index = Column(String(50), nullable=True) # Good, Fair, Poor
    diagnosis = Column(Text, nullable=True)
    clinical_notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    patient = relationship("Patient", back_populates="visits")
    dentist = relationship("Dentist", back_populates="visits")
    appointment = relationship("Appointment", back_populates="visit")

    tooth_conditions = relationship("ToothConditionHistory", back_populates="visit")
    treatments = relationship("TreatmentItem", back_populates="visit")
    prescriptions = relationship("Prescription", back_populates="visit")
    documents = relationship("Document", back_populates="visit")
    invoices = relationship("Invoice", back_populates="visit")
    followups = relationship("FollowUp", back_populates="visit")
