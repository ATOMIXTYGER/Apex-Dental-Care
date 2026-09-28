from pathlib import Path

from fastapi import HTTPException, Request, UploadFile, status
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.audit.service import log_audit_event
from app.models.document import Document
from app.models.patient import Patient
from app.models.user import User
from app.storage.file_storage import file_storage


class DocumentService:
    @staticmethod
    async def upload_document(
        db: Session,
        patient_id: int,
        document_type: str,
        file: UploadFile,
        current_user: User,
        visit_id: int | None = None,
        notes: str | None = None,
        request: Request | None = None
    ) -> Document:
        patient = db.query(Patient).filter(Patient.id == patient_id, Patient.is_deleted == False).first()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "PATIENT_NOT_FOUND", "message": "Patient not found."}
            )

        stored_name, orig_name, size_bytes, mime = await file_storage.save_file(file)

        doc = Document(
            patient_id=patient_id,
            visit_id=visit_id,
            document_type=document_type,
            file_name=stored_name,
            original_file_name=orig_name,
            file_size=size_bytes,
            mime_type=mime,
            file_path=str(file_storage.get_file_path(stored_name)),
            notes=notes,
            uploaded_by_user_id=current_user.id
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        log_audit_event(
            db=db,
            action="DOCUMENT_UPLOAD",
            user=current_user,
            entity_name="Document",
            entity_id=str(doc.id),
            details={"patient_id": patient_id, "type": document_type, "filename": orig_name},
            request=request
        )

        return doc

    @staticmethod
    def get_document_by_id(db: Session, document_id: int) -> Document:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "DOCUMENT_NOT_FOUND", "message": "Document not found."}
            )
        return doc

    @staticmethod
    def get_patient_documents(db: Session, patient_id: int) -> list[Document]:
        return db.query(Document).filter(Document.patient_id == patient_id).order_by(desc(Document.created_at)).all()

    @staticmethod
    def get_all_documents(db: Session, document_type: str | None = None) -> list[Document]:
        query = db.query(Document)
        if document_type:
            query = query.filter(Document.document_type == document_type)
        return query.order_by(desc(Document.created_at)).all()

    @classmethod
    def get_file_path(cls, db: Session, document_id: int, current_user: User, request: Request | None = None) -> Path:
        doc = cls.get_document_by_id(db, document_id)
        path = file_storage.get_file_path(doc.file_name)

        log_audit_event(
            db=db,
            action="DOCUMENT_DOWNLOAD",
            user=current_user,
            entity_name="Document",
            entity_id=str(doc.id),
            details={"filename": doc.original_file_name},
            request=request
        )

        return path
