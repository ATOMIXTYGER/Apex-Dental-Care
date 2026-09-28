from datetime import datetime, UTC

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    user_email = Column(String(255), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)
    # CREATE, UPDATE, DELETE, LOGIN, LOGOUT, LOGIN_FAILURE, PASSWORD_CHANGE,
    # PATIENT_VIEW, DOCUMENT_UPLOAD, DOCUMENT_DOWNLOAD, PRESCRIPTION_CREATE,
    # INVOICE_CREATE, PAYMENT_CREATE, ROLE_CHANGE
    entity_name = Column(String(100), nullable=True, index=True) # e.g. Patient, Appointment, Invoice, ToothCondition
    entity_id = Column(String(100), nullable=True, index=True)
    details = Column(Text, nullable=True) # Sanitized JSON or text description
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False, index=True)

    user = relationship("User")
