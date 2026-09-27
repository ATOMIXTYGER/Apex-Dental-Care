from decimal import Decimal
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi import HTTPException, status, Request

from app.models.treatment import TreatmentPlan, TreatmentItem, ProcedureCatalog
from app.models.patient import Patient
from app.models.user import Dentist, User
from app.schemas.treatment import (
    TreatmentPlanCreate, TreatmentPlanUpdate, TreatmentItemCreate, TreatmentItemUpdate
)
from app.audit.service import log_audit_event

class TreatmentService:
    @staticmethod
    def calculate_plan_total(plan: TreatmentPlan) -> Decimal:
        """Compute sum of treatments using exact Decimal arithmetic."""
        total = Decimal('0.00')
        for item in plan.treatments:
            if item.status != "cancelled":
                # Use actual_cost if set, otherwise estimated_cost
                cost = item.actual_cost if item.actual_cost and item.actual_cost > 0 else item.estimated_cost
                total += Decimal(str(cost))
        return total

    @classmethod
    def create_treatment_plan(
        cls,
        db: Session,
        data: TreatmentPlanCreate,
        current_user: User,
        request: Optional[Request] = None
    ) -> TreatmentPlan:
        """Create a treatment plan with multiple treatment items."""
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

        plan = TreatmentPlan(
            patient_id=data.patient_id,
            dentist_id=data.dentist_id,
            title=data.title,
            status="active",
            estimated_total=Decimal('0.00'),
            notes=data.notes
        )
        db.add(plan)
        db.flush()

        # Add treatments
        for item_data in data.treatments:
            item = TreatmentItem(
                treatment_plan_id=plan.id,
                procedure_name=item_data.procedure_name,
                tooth_number=item_data.tooth_number,
                estimated_cost=item_data.estimated_cost,
                actual_cost=Decimal('0.00'),
                status="planned",
                notes=item_data.notes
            )
            db.add(item)
            plan.treatments.append(item)

        plan.estimated_total = cls.calculate_plan_total(plan)
        db.commit()
        db.refresh(plan)

        log_audit_event(
            db=db,
            action="CREATE",
            user=current_user,
            entity_name="TreatmentPlan",
            entity_id=str(plan.id),
            details={"patient_id": plan.patient_id, "title": plan.title, "total": str(plan.estimated_total)},
            request=request
        )

        return plan

    @staticmethod
    def get_plans(
        db: Session,
        patient_id: Optional[int] = None,
        dentist_id: Optional[int] = None,
        status_filter: Optional[str] = None
    ) -> List[TreatmentPlan]:
        query = db.query(TreatmentPlan)
        if patient_id:
            query = query.filter(TreatmentPlan.patient_id == patient_id)
        if dentist_id:
            query = query.filter(TreatmentPlan.dentist_id == dentist_id)
        if status_filter:
            query = query.filter(TreatmentPlan.status == status_filter)
        return query.order_by(desc(TreatmentPlan.created_at)).all()

    @staticmethod
    def get_plan_by_id(db: Session, plan_id: int) -> TreatmentPlan:
        plan = db.query(TreatmentPlan).filter(TreatmentPlan.id == plan_id).first()
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "PLAN_NOT_FOUND", "message": f"Treatment plan {plan_id} not found."}
            )
        return plan

    @classmethod
    def add_treatment_item(
        cls,
        db: Session,
        plan_id: int,
        data: TreatmentItemCreate,
        current_user: User,
        request: Optional[Request] = None
    ) -> TreatmentItem:
        plan = cls.get_plan_by_id(db, plan_id)
        item = TreatmentItem(
            treatment_plan_id=plan.id,
            procedure_name=data.procedure_name,
            tooth_number=data.tooth_number,
            estimated_cost=data.estimated_cost,
            actual_cost=Decimal('0.00'),
            status="planned",
            notes=data.notes
        )
        db.add(item)
        plan.treatments.append(item)
        plan.estimated_total = cls.calculate_plan_total(plan)
        db.commit()
        db.refresh(item)

        log_audit_event(
            db=db,
            action="TREATMENT_ADD",
            user=current_user,
            entity_name="TreatmentItem",
            entity_id=str(item.id),
            details={"plan_id": plan.id, "procedure": item.procedure_name},
            request=request
        )

        return item

    @classmethod
    def update_treatment_item(
        cls,
        db: Session,
        item_id: int,
        data: TreatmentItemUpdate,
        current_user: User,
        request: Optional[Request] = None
    ) -> TreatmentItem:
        item = db.query(TreatmentItem).filter(TreatmentItem.id == item_id).first()
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "ITEM_NOT_FOUND", "message": "Treatment item not found."}
            )

        update_dict = data.model_dump(exclude_unset=True)
        if data.status == "completed" and item.status != "completed":
            item.completed_at = datetime.now(timezone.utc)

        for k, v in update_dict.items():
            setattr(item, k, v)

        # Recalculate plan total
        item.treatment_plan.estimated_total = cls.calculate_plan_total(item.treatment_plan)
        db.commit()
        db.refresh(item)

        log_audit_event(
            db=db,
            action="TREATMENT_UPDATE",
            user=current_user,
            entity_name="TreatmentItem",
            entity_id=str(item.id),
            details={"status": item.status, "procedure": item.procedure_name},
            request=request
        )

        return item
