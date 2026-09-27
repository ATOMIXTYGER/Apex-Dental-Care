from typing import Optional, List
from fastapi import APIRouter, Depends, status, UploadFile, File, Form, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.document import DocumentResponse
from app.services.document_service import DocumentService
from app.security.dependencies import get_current_user, require_roles

router = APIRouter(prefix="/documents", tags=["Document & X-Ray Management"])

@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    request: Request,
    patient_id: int = Form(...),
    document_type: str = Form(...),
    notes: Optional[str] = Form(None),
    visit_id: Optional[int] = Form(None),
    file: UploadFile = File(...),
    current_user: User = Depends(require_roles("admin", "dentist", "receptionist")),
    db: Session = Depends(get_db)
):
    """Securely upload patient document or diagnostic X-ray image."""
    doc = await DocumentService.upload_document(
        db=db,
        patient_id=patient_id,
        document_type=document_type,
        file=file,
        current_user=current_user,
        visit_id=visit_id,
        notes=notes,
        request=request
    )
    resp = DocumentResponse.model_validate(doc)
    resp.patient_name = doc.patient.full_name if doc.patient else None
    return resp

@router.get("", response_model=List[DocumentResponse])
def list_documents(
    document_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve all clinic documents and X-rays with optional type filter."""
    docs = DocumentService.get_all_documents(db, document_type=document_type)
    result = []
    for d in docs:
        resp = DocumentResponse.model_validate(d)
        resp.patient_name = d.patient.full_name if d.patient else None
        result.append(resp)
    return result

@router.get("/patient/{patient_id}", response_model=List[DocumentResponse])
def get_patient_documents(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve metadata of all documents and X-rays for a patient."""
    docs = DocumentService.get_patient_documents(db, patient_id)
    result = []
    for d in docs:
        resp = DocumentResponse.model_validate(d)
        resp.patient_name = d.patient.full_name if d.patient else None
        result.append(resp)
    return result

@router.get("/{document_id}/download")
def download_document(
    request: Request,
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Stream protected file securely after verifying authorization."""
    doc = DocumentService.get_document_by_id(db, document_id)
    file_path = DocumentService.get_file_path(db, document_id, current_user=current_user, request=request)

    return FileResponse(
        path=file_path,
        media_type=doc.mime_type,
        filename=doc.original_file_name,
        headers={
            "Content-Disposition": f'inline; filename="{doc.original_file_name}"'
        }
    )
