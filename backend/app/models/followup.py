from datetime import datetime, UTC

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class FollowUp(Base):
    __tablename__ = "followups"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    dentist_id = Column(Integer, ForeignKey("dentists.id", ondelete="RESTRICT"), nullable=False, index=True)
    visit_id = Column(Integer, ForeignKey("visits.id", ondelete="SET NULL"), nullable=True)
    scheduled_date = Column(Date, nullable=False, index=True)
    reason = Column(String(255), nullable=False)
    status = Column(String(50), default="pending", nullable=False, index=True) # pending, completed, cancelled
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    patient = relationship("Patient", back_populates="followups")
    dentist = relationship("Dentist")
    visit = relationship("Visit", back_populates="followups")
