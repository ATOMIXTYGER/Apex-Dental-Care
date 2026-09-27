from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

# FDI permanent teeth set: 11-18, 21-28, 31-38, 41-48
FDI_PERMANENT_TEETH = {
    18, 17, 16, 15, 14, 13, 12, 11,
    21, 22, 23, 24, 25, 26, 27, 28,
    38, 37, 36, 35, 34, 33, 32, 31,
    41, 42, 43, 44, 45, 46, 47, 48,
}

class ToothCondition(Base):
    """Represents the CURRENT state of a tooth for a patient."""
    __tablename__ = "tooth_conditions"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    tooth_number = Column(Integer, nullable=False, index=True) # 11-48
    current_condition = Column(String(50), nullable=False, default="healthy") 
    # healthy, caries, missing, filled, crown, root_canal, extraction, fracture, sensitivity, mobility, bridge, implant, impacted, other
    severity = Column(String(50), nullable=True, default="none") # none, mild, moderate, severe
    surfaces = Column(String(50), nullable=True) # e.g. "MODBL", "O", "MO"
    notes = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        UniqueConstraint('patient_id', 'tooth_number', name='uq_patient_tooth'),
    )

    patient = relationship("Patient", back_populates="tooth_conditions")

class ToothConditionHistory(Base):
    """Historical timeline of changes made to tooth conditions during visits."""
    __tablename__ = "tooth_condition_histories"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    visit_id = Column(Integer, ForeignKey("visits.id", ondelete="SET NULL"), nullable=True, index=True)
    dentist_id = Column(Integer, ForeignKey("dentists.id", ondelete="RESTRICT"), nullable=False)
    tooth_number = Column(Integer, nullable=False, index=True)
    condition = Column(String(50), nullable=False)
    severity = Column(String(50), nullable=True)
    surfaces = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    visit = relationship("Visit", back_populates="tooth_conditions")
    dentist = relationship("Dentist")
