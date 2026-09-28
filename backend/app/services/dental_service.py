
from fastapi import HTTPException, Request, status
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.audit.service import log_audit_event
from app.models.dental_chart import (
    FDI_PERMANENT_TEETH,
    ToothCondition,
    ToothConditionHistory,
)
from app.models.patient import Patient
from app.models.user import Dentist, User
from app.schemas.dental_chart import (
    DentalChartDetailResponse,
    ToothConditionResponse,
    ToothConditionUpdate,
    ToothHistoryResponse,
)


class DentalChartService:
    @staticmethod
    def get_or_create_patient_chart(db: Session, patient_id: int) -> dict[int, ToothCondition]:
        """
        Retrieve all 32 permanent teeth conditions for a patient.
        If a tooth condition record doesn't exist yet, it's lazily or initially populated as 'healthy'.
        """
        # Verify patient exists
        patient = db.query(Patient).filter(Patient.id == patient_id, Patient.is_deleted == False).first()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "PATIENT_NOT_FOUND", "message": "Patient not found."}
            )

        existing = db.query(ToothCondition).filter(ToothCondition.patient_id == patient_id).all()
        chart_map = {t.tooth_number: t for t in existing}

        # Initialize any missing permanent teeth as healthy
        missing_teeth = FDI_PERMANENT_TEETH - set(chart_map.keys())
        if missing_teeth:
            new_teeth = []
            for tooth_num in missing_teeth:
                tc = ToothCondition(
                    patient_id=patient_id,
                    tooth_number=tooth_num,
                    current_condition="healthy",
                    severity="none"
                )
                db.add(tc)
                new_teeth.append(tc)
            db.commit()
            for tc in new_teeth:
                chart_map[tc.tooth_number] = tc

        return chart_map

    @classmethod
    def update_tooth_condition(
        cls,
        db: Session,
        patient_id: int,
        data: ToothConditionUpdate,
        current_user: User,
        request: Request | None = None
    ) -> ToothCondition:
        """
        Update the current condition of a tooth and log an immutable history snapshot.
        Must be performed by a dentist or admin.
        """
        if data.tooth_number not in FDI_PERMANENT_TEETH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "INVALID_TOOTH", "message": f"Tooth {data.tooth_number} is not a valid FDI permanent tooth."}
            )

        # Get or resolve dentist ID
        dentist_id = None
        if current_user.dentist_profile:
            dentist_id = current_user.dentist_profile.id
        else:
            # Fallback to first active dentist or admin
            first_dentist = db.query(Dentist).filter(Dentist.is_active == True).first()
            if first_dentist:
                dentist_id = first_dentist.id

        if not dentist_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "NO_DENTIST_CONTEXT", "message": "A dentist profile is required to record dental conditions."}
            )

        # Find or create condition
        tooth_cond = db.query(ToothCondition).filter(
            ToothCondition.patient_id == patient_id,
            ToothCondition.tooth_number == data.tooth_number
        ).first()

        if not tooth_cond:
            tooth_cond = ToothCondition(
                patient_id=patient_id,
                tooth_number=data.tooth_number,
                current_condition=data.condition,
                severity=data.severity or "none",
                surfaces=data.surfaces,
                notes=data.notes
            )
            db.add(tooth_cond)
        else:
            tooth_cond.current_condition = data.condition
            tooth_cond.severity = data.severity or "none"
            tooth_cond.surfaces = data.surfaces
            tooth_cond.notes = data.notes

        # Create immutable history entry
        history_entry = ToothConditionHistory(
            patient_id=patient_id,
            visit_id=data.visit_id,
            dentist_id=dentist_id,
            tooth_number=data.tooth_number,
            condition=data.condition,
            severity=data.severity,
            surfaces=data.surfaces,
            notes=data.notes
        )
        db.add(history_entry)
        db.commit()
        db.refresh(tooth_cond)

        log_audit_event(
            db=db,
            action="TOOTH_UPDATE",
            user=current_user,
            entity_name="ToothCondition",
            entity_id=f"{patient_id}-{data.tooth_number}",
            details={"condition": data.condition, "severity": data.severity, "surfaces": data.surfaces},
            request=request
        )

        return tooth_cond

    @staticmethod
    def get_tooth_history(db: Session, patient_id: int, tooth_number: int | None = None) -> list[ToothConditionHistory]:
        """Fetch history entries for a specific tooth or all teeth of a patient."""
        query = db.query(ToothConditionHistory).filter(ToothConditionHistory.patient_id == patient_id)
        if tooth_number:
            query = query.filter(ToothConditionHistory.tooth_number == tooth_number)
        return query.order_by(desc(ToothConditionHistory.created_at)).all()

    @staticmethod
    def get_full_chart_details(db: Session, patient_id: int) -> DentalChartDetailResponse:
        """Fetch entire 32-tooth state, history, and active treatments."""
        chart_map = DentalChartService.get_or_create_patient_chart(db, patient_id)
        history_records = DentalChartService.get_tooth_history(db, patient_id)

        history_list = []
        for h in history_records:
            history_list.append(ToothHistoryResponse(
                id=h.id,
                patient_id=h.patient_id,
                visit_id=h.visit_id,
                dentist_id=h.dentist_id,
                dentist_name=h.dentist.user.full_name if h.dentist and h.dentist.user else None,
                tooth_number=h.tooth_number,
                condition=h.condition,
                severity=h.severity,
                surfaces=h.surfaces,
                notes=h.notes,
                created_at=h.created_at
            ))

        teeth_dict = {
            t_num: ToothConditionResponse.model_validate(tc) for t_num, tc in chart_map.items()
        }

        return DentalChartDetailResponse(
            patient_id=patient_id,
            teeth=teeth_dict,
            history=history_list
        )
