from datetime import datetime, UTC

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    visit_id = Column(Integer, ForeignKey("visits.id", ondelete="SET NULL"), nullable=True, index=True)
    document_type = Column(String(50), nullable=False) # xray, opg, cbct, photo, lab_report, consent_form, other
    file_name = Column(String(255), nullable=False) # unique server-side generated filename (UUID based)
    original_file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False) # in bytes
    mime_type = Column(String(100), nullable=False)
    file_path = Column(String(500), nullable=False)
    notes = Column(Text, nullable=True)
    uploaded_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    patient = relationship("Patient", back_populates="documents")
    visit = relationship("Visit", back_populates="documents")
    uploaded_by = relationship("User")
