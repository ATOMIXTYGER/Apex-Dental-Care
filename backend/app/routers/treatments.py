
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.treatment import ProcedureCatalog
from app.models.user import User
from app.schemas.treatment import (
    ProcedureCatalogResponse,
    TreatmentItemCreate,
    TreatmentItemResponse,
    TreatmentItemUpdate,
    TreatmentPlanCreate,
    TreatmentPlanResponse,
)
from app.security.dependencies import get_current_user, require_roles
from app.services.treatment_service import TreatmentService

router = APIRouter(prefix="/treatments", tags=["Treatment Management"])

@router.get("/catalog", response_model=list[ProcedureCatalogResponse])
def get_procedure_catalog(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve catalog of standard dental procedures with default costs."""
    catalog = db.query(ProcedureCatalog).order_by(ProcedureCatalog.category, ProcedureCatalog.name).all()
    return [ProcedureCatalogResponse.model_validate(c) for c in catalog]

@router.get("/plans", response_model=list[TreatmentPlanResponse])
def list_treatment_plans(
    patient_id: int | None = None,
    dentist_id: int | None = None,
    status: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List treatment plans with optional patient, dentist, or status filters."""
    plans = TreatmentService.get_plans(db, patient_id=patient_id, dentist_id=dentist_id, status_filter=status)
    result = []
    for p in plans:
        resp = TreatmentPlanResponse.model_validate(p)
        resp.patient_name = p.patient.full_name if p.patient else None
        resp.dentist_name = p.dentist.user.full_name if p.dentist and p.dentist.user else None
        result.append(resp)
    return result

@router.post("/plans", response_model=TreatmentPlanResponse, status_code=status.HTTP_201_CREATED)
def create_treatment_plan(
    request: Request,
    payload: TreatmentPlanCreate,
    current_user: User = Depends(require_roles("dentist", "admin")),
    db: Session = Depends(get_db)
):
    """Dentist-only: Create a multi-procedure treatment plan."""
    plan = TreatmentService.create_treatment_plan(db, data=payload, current_user=current_user, request=request)
    resp = TreatmentPlanResponse.model_validate(plan)
    resp.patient_name = plan.patient.full_name if plan.patient else None
    resp.dentist_name = plan.dentist.user.full_name if plan.dentist and plan.dentist.user else None
    return resp

@router.get("/plans/{plan_id}", response_model=TreatmentPlanResponse)
def get_treatment_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve full treatment plan details and item progress."""
    plan = TreatmentService.get_plan_by_id(db, plan_id)
    resp = TreatmentPlanResponse.model_validate(plan)
    resp.patient_name = plan.patient.full_name if plan.patient else None
    resp.dentist_name = plan.dentist.user.full_name if plan.dentist and plan.dentist.user else None
    return resp

@router.post("/plans/{plan_id}/items", response_model=TreatmentItemResponse)
def add_treatment_item(
    request: Request,
    plan_id: int,
    payload: TreatmentItemCreate,
    current_user: User = Depends(require_roles("dentist", "admin")),
    db: Session = Depends(get_db)
):
    """Dentist-only: Add a new procedure item to an existing plan."""
    item = TreatmentService.add_treatment_item(db, plan_id=plan_id, data=payload, current_user=current_user, request=request)
    return TreatmentItemResponse.model_validate(item)

@router.put("/items/{item_id}", response_model=TreatmentItemResponse)
def update_treatment_item(
    request: Request,
    item_id: int,
    payload: TreatmentItemUpdate,
    current_user: User = Depends(require_roles("dentist", "admin")),
    db: Session = Depends(get_db)
):
    """Dentist-only: Update procedure status (planned, in_progress, completed) or actual cost."""
    item = TreatmentService.update_treatment_item(db, item_id=item_id, data=payload, current_user=current_user, request=request)
    return TreatmentItemResponse.model_validate(item)
