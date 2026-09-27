from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi import HTTPException, status, Request

from app.models.clinical import Visit
from app.models.appointment import Appointment
from app.models.patient import Patient
from app.models.user import Dentist, User
from app.schemas.clinical import VisitCreate, VisitUpdate
from app.audit.service import log_audit_event

class ClinicalService:
    @staticmethod
    def create_visit(
        db: Session,
        data: VisitCreate,
        current_user: User,
        request: Optional[Request] = None
    ) -> Visit:
        """Record a dental visit and clinical examination."""
        # Validate patient
        patient = db.query(Patient).filter(Patient.id == data.patient_id, Patient.is_deleted == False).first()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "PATIENT_NOT_FOUND", "message": "Patient does not exist."}
            )

        # Validate dentist
        dentist = db.query(Dentist).filter(Dentist.id == data.dentist_id).first()
        if not dentist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "DENTIST_NOT_FOUND", "message": "Dentist does not exist."}
            )

        # If linked to appointment, verify and update appointment status
        if data.appointment_id:
            appt = db.query(Appointment).filter(Appointment.id == data.appointment_id).first()
            if appt:
                appt.status = "completed"

        visit = Visit(
            patient_id=data.patient_id,
            dentist_id=data.dentist_id,
            appointment_id=data.appointment_id,
            visit_date=data.visit_date,
            vitals_blood_pressure=data.vitals_blood_pressure,
            vitals_pulse=data.vitals_pulse,
            chief_complaint=data.chief_complaint,
            oral_findings=data.oral_findings,
            gum_condition=data.gum_condition,
            hygiene_index=data.hygiene_index,
            diagnosis=data.diagnosis,
            clinical_notes=data.clinical_notes
        )
        db.add(visit)
        db.commit()
        db.refresh(visit)

        log_audit_event(
            db=db,
            action="CREATE",
            user=current_user,
            entity_name="Visit",
            entity_id=str(visit.id),
            details={"patient_id": visit.patient_id, "diagnosis": visit.diagnosis},
            request=request
        )

        return visit

    @staticmethod
    def get_visit_by_id(db: Session, visit_id: int) -> Visit:
        visit = db.query(Visit).filter(Visit.id == visit_id).first()
        if not visit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "VISIT_NOT_FOUND", "message": f"Visit with ID {visit_id} was not found."}
            )
        return visit

    @staticmethod
    def get_patient_visits(db: Session, patient_id: int) -> List[Visit]:
        return db.query(Visit).filter(Visit.patient_id == patient_id).order_by(desc(Visit.visit_date)).all()

    @staticmethod
    def update_visit(
        db: Session,
        visit_id: int,
        data: VisitUpdate,
        current_user: User,
        request: Optional[Request] = None
    ) -> Visit:
        visit = ClinicalService.get_visit_by_id(db, visit_id)
        update_dict = data.model_dump(exclude_unset=True)
        for k, v in update_dict.items():
            setattr(visit, k, v)
        db.commit()
        db.refresh(visit)

        log_audit_event(
            db=db,
            action="UPDATE",
            user=current_user,
            entity_name="Visit",
            entity_id=str(visit.id),
            details={"updated_fields": list(update_dict.keys())},
            request=request
        )

        return visit
