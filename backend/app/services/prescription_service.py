from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from fastapi import HTTPException, status, Request

from app.models.prescription import Prescription, PrescriptionItem
from app.models.patient import Patient
from app.models.user import Dentist, User
from app.schemas.prescription import PrescriptionCreate
from app.pdf.generator import generate_prescription_pdf
from app.audit.service import log_audit_event

class PrescriptionService:
    @staticmethod
    def _generate_rx_number(db: Session) -> str:
        count = db.query(func.count(Prescription.id)).scalar() or 0
        return f"RX-2026-{1001 + count}"

    @classmethod
    def create_prescription(
        cls,
        db: Session,
        data: PrescriptionCreate,
        current_user: User,
        request: Optional[Request] = None
    ) -> Prescription:
        patient = db.query(Patient).filter(Patient.id == data.patient_id, Patient.is_deleted == False).first()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "PATIENT_NOT_FOUND", "message": "Patient not found."}
            )

        dentist = db.query(Dentist).filter(Dentist.id == data.dentist_id).first()
        if not dentist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "DENTIST_NOT_FOUND", "message": "Dentist not found."}
            )

        rx_number = cls._generate_rx_number(db)
        prescription = Prescription(
            prescription_number=rx_number,
            patient_id=data.patient_id,
            dentist_id=data.dentist_id,
            visit_id=data.visit_id,
            diagnosis_summary=data.diagnosis_summary,
            general_instructions=data.general_instructions
        )
        db.add(prescription)
        db.flush()

        for item_data in data.items:
            item = PrescriptionItem(
                prescription_id=prescription.id,
                medicine_name=item_data.medicine_name,
                dosage=item_data.dosage,
                frequency=item_data.frequency,
                duration=item_data.duration,
                timing=item_data.timing,
                instructions=item_data.instructions
            )
            db.add(item)

        db.commit()
        db.refresh(prescription)

        log_audit_event(
            db=db,
            action="PRESCRIPTION_CREATE",
            user=current_user,
            entity_name="Prescription",
            entity_id=str(prescription.id),
            details={"rx_number": prescription.prescription_number, "items_count": len(data.items)},
            request=request
        )

        return prescription

    @staticmethod
    def get_prescriptions(
        db: Session,
        patient_id: Optional[int] = None,
        dentist_id: Optional[int] = None
    ) -> List[Prescription]:
        query = db.query(Prescription)
        if patient_id:
            query = query.filter(Prescription.patient_id == patient_id)
        if dentist_id:
            query = query.filter(Prescription.dentist_id == dentist_id)
        return query.order_by(desc(Prescription.created_at)).all()

    @staticmethod
    def get_prescription_by_id(db: Session, prescription_id: int) -> Prescription:
        rx = db.query(Prescription).filter(Prescription.id == prescription_id).first()
        if not rx:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "PRESCRIPTION_NOT_FOUND", "message": "Prescription not found."}
            )
        return rx

    @classmethod
    def get_pdf(cls, db: Session, prescription_id: int) -> bytes:
        rx = cls.get_prescription_by_id(db, prescription_id)
        return generate_prescription_pdf(rx, rx.patient, rx.dentist)
