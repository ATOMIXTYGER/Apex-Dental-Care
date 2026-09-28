from datetime import datetime, UTC

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text, Time
from sqlalchemy.orm import relationship

from app.database import Base


class AppointmentType(Base):
    __tablename__ = "appointment_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    duration_minutes = Column(Integer, default=30, nullable=False)
    color_code = Column(String(20), default="#14b8a6", nullable=False)
    default_fee = Column(Integer, default=0, nullable=False)

    appointments = relationship("Appointment", back_populates="appointment_type")

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="RESTRICT"), nullable=False, index=True)
    dentist_id = Column(Integer, ForeignKey("dentists.id", ondelete="RESTRICT"), nullable=False, index=True)
    appointment_type_id = Column(Integer, ForeignKey("appointment_types.id", ondelete="SET NULL"), nullable=True)
    appointment_date = Column(Date, nullable=False, index=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    status = Column(String(50), default="scheduled", nullable=False, index=True) # scheduled, confirmed, in_progress, completed, cancelled, no_show
    reason = Column(String(255), nullable=True)
    cancellation_reason = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    patient = relationship("Patient", back_populates="appointments")
    dentist = relationship("Dentist", back_populates="appointments")
    appointment_type = relationship("AppointmentType", back_populates="appointments")
    visit = relationship("Visit", back_populates="appointment", uselist=False)
