from typing import Optional, List
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi import HTTPException, status, Request

from app.models.followup import FollowUp
from app.models.patient import Patient
from app.models.user import Dentist, User
from app.schemas.followup import FollowUpCreate, FollowUpUpdate
from app.audit.service import log_audit_event

class FollowUpService:
    @staticmethod
    def create_followup(
        db: Session,
        data: FollowUpCreate,
        current_user: User,
        request: Optional[Request] = None
    ) -> FollowUp:
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

        followup = FollowUp(
            patient_id=data.patient_id,
            dentist_id=data.dentist_id,
            visit_id=data.visit_id,
            scheduled_date=data.scheduled_date,
            reason=data.reason,
            status="pending",
            notes=data.notes
        )
        db.add(followup)
        db.commit()
        db.refresh(followup)

        log_audit_event(
            db=db,
            action="CREATE",
            user=current_user,
            entity_name="FollowUp",
            entity_id=str(followup.id),
            details={"patient_id": followup.patient_id, "scheduled_date": str(followup.scheduled_date)},
            request=request
        )

        return followup

    @staticmethod
    def get_followups(
        db: Session,
        patient_id: Optional[int] = None,
        dentist_id: Optional[int] = None,
        status_filter: Optional[str] = None
    ) -> List[FollowUp]:
        query = db.query(FollowUp)
        if patient_id:
            query = query.filter(FollowUp.patient_id == patient_id)
        if dentist_id:
            query = query.filter(FollowUp.dentist_id == dentist_id)
        if status_filter:
            query = query.filter(FollowUp.status == status_filter)
        return query.order_by(FollowUp.scheduled_date.asc()).all()

    @staticmethod
    def update_followup(
        db: Session,
        followup_id: int,
        data: FollowUpUpdate,
        current_user: User,
        request: Optional[Request] = None
    ) -> FollowUp:
        fu = db.query(FollowUp).filter(FollowUp.id == followup_id).first()
        if not fu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "FOLLOWUP_NOT_FOUND", "message": "Follow-up record not found."}
            )

        update_dict = data.model_dump(exclude_unset=True)
        for k, v in update_dict.items():
            setattr(fu, k, v)

        db.commit()
        db.refresh(fu)

        log_audit_event(
            db=db,
            action="UPDATE",
            user=current_user,
            entity_name="FollowUp",
            entity_id=str(fu.id),
            details={"status": fu.status},
            request=request
        )

        return fu
