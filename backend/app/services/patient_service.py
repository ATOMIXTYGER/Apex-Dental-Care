from typing import Optional, Dict, Any, Tuple, List
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, func
from fastapi import HTTPException, status, Request

from app.models.patient import Patient, MedicalHistory, DentalHistory
from app.models.user import User
from app.schemas.patient import PatientCreate, PatientUpdate
from app.audit.service import log_audit_event

class PatientService:
    @staticmethod
    def _generate_patient_code(db: Session) -> str:
        """Generate a sequential unique patient ID like P-1001, P-1002."""
        count = db.query(func.count(Patient.id)).scalar() or 0
        return f"P-{1001 + count}"

    @classmethod
    def create_patient(
        cls,
        db: Session,
        data: PatientCreate,
        current_user: User,
        request: Optional[Request] = None
    ) -> Patient:
        """Register a new patient along with optional medical and dental histories in one transaction."""
        patient_code = cls._generate_patient_code(db)

        # Check existing email/phone if appropriate
        existing_phone = db.query(Patient).filter(Patient.phone == data.phone, Patient.is_deleted == False).first()
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "DUPLICATE_PHONE", "message": f"A patient with phone {data.phone} already exists."}
            )

        new_patient = Patient(
            patient_code=patient_code,
            first_name=data.first_name,
            last_name=data.last_name,
            date_of_birth=data.date_of_birth,
            gender=data.gender,
            phone=data.phone,
            email=data.email,
            address=data.address,
            emergency_contact_name=data.emergency_contact_name,
            emergency_contact_phone=data.emergency_contact_phone,
            blood_group=data.blood_group,
            is_deleted=False
        )
        db.add(new_patient)
        db.flush() # Flush to acquire patient ID

        # Optional Medical History
        if data.medical_history:
            med_hist = MedicalHistory(
                patient_id=new_patient.id,
                allergies=data.medical_history.allergies,
                medical_conditions=data.medical_history.medical_conditions,
                current_medications=data.medical_history.current_medications,
                past_surgeries=data.medical_history.past_surgeries,
                bleeding_disorders=data.medical_history.bleeding_disorders,
                is_pregnant=data.medical_history.is_pregnant,
                notes=data.medical_history.notes
            )
            db.add(med_hist)
        else:
            db.add(MedicalHistory(patient_id=new_patient.id))

        # Optional Dental History
        if data.dental_history:
            dent_hist = DentalHistory(
                patient_id=new_patient.id,
                chief_complaint=data.dental_history.chief_complaint,
                past_dental_treatments=data.dental_history.past_dental_treatments,
                brushing_frequency=data.dental_history.brushing_frequency,
                flossing=data.dental_history.flossing,
                habits=data.dental_history.habits,
                dental_anxiety_level=data.dental_history.dental_anxiety_level,
                notes=data.dental_history.notes
            )
            db.add(dent_hist)
        else:
            db.add(DentalHistory(patient_id=new_patient.id))

        db.commit()
        db.refresh(new_patient)

        log_audit_event(
            db=db,
            action="CREATE",
            user=current_user,
            entity_name="Patient",
            entity_id=str(new_patient.id),
            details={"patient_code": new_patient.patient_code, "name": new_patient.full_name},
            request=request
        )

        return new_patient

    @staticmethod
    def get_patients_paginated(
        db: Session,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None
    ) -> Tuple[List[Patient], int]:
        """Search and paginate patients (by code, first/last name, phone)."""
        query = db.query(Patient).filter(Patient.is_deleted == False)

        if search:
            search_term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Patient.patient_code.ilike(search_term),
                    Patient.first_name.ilike(search_term),
                    Patient.last_name.ilike(search_term),
                    Patient.phone.ilike(search_term)
                )
            )

        total = query.count()
        items = query.order_by(desc(Patient.created_at)).offset((page - 1) * page_size).limit(page_size).all()
        return items, total

    @staticmethod
    def get_patient_by_id(db: Session, patient_id: int) -> Patient:
        """Retrieve patient details or raise 404."""
        patient = db.query(Patient).filter(Patient.id == patient_id, Patient.is_deleted == False).first()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "PATIENT_NOT_FOUND", "message": f"Patient with ID {patient_id} does not exist."}
            )
        return patient

    @staticmethod
    def update_patient(
        db: Session,
        patient_id: int,
        data: PatientUpdate,
        current_user: User,
        request: Optional[Request] = None
    ) -> Patient:
        """Update patient demographics or medical/dental history."""
        patient = PatientService.get_patient_by_id(db, patient_id)

        update_dict = data.model_dump(exclude_unset=True)
        med_data = update_dict.pop("medical_history", None)
        dent_data = update_dict.pop("dental_history", None)

        for k, v in update_dict.items():
            setattr(patient, k, v)

        if med_data is not None:
            if not patient.medical_history:
                patient.medical_history = MedicalHistory(patient_id=patient.id)
            for mk, mv in med_data.items():
                if mv is not None:
                    setattr(patient.medical_history, mk, mv)

        if dent_data is not None:
            if not patient.dental_history:
                patient.dental_history = DentalHistory(patient_id=patient.id)
            for dk, dv in dent_data.items():
                if dv is not None:
                    setattr(patient.dental_history, dk, dv)

        db.commit()
        db.refresh(patient)

        log_audit_event(
            db=db,
            action="UPDATE",
            user=current_user,
            entity_name="Patient",
            entity_id=str(patient.id),
            details={"updated_fields": list(update_dict.keys())},
            request=request
        )

        return patient

    @staticmethod
    def soft_delete_patient(
        db: Session,
        patient_id: int,
        current_user: User,
        request: Optional[Request] = None
    ):
        """Soft delete patient to preserve clinical records."""
        patient = PatientService.get_patient_by_id(db, patient_id)
        patient.is_deleted = True
        db.commit()

        log_audit_event(
            db=db,
            action="DELETE",
            user=current_user,
            entity_name="Patient",
            entity_id=str(patient.id),
            details="Patient soft-deleted",
            request=request
        )

    @staticmethod
    def get_patient_timeline(db: Session, patient_id: int) -> List[Dict[str, Any]]:
        """Consolidate timeline of events across visits, treatments, prescriptions, and appointments."""
        patient = PatientService.get_patient_by_id(db, patient_id)
        events = []

        # Appointments
        for appt in patient.appointments:
            events.append({
                "type": "appointment",
                "id": appt.id,
                "date": appt.appointment_date.isoformat(),
                "title": f"Appointment: {appt.appointment_type.name if appt.appointment_type else 'General'}",
                "status": appt.status,
                "notes": appt.notes or appt.reason,
                "dentist": appt.dentist.user.full_name if appt.dentist and appt.dentist.user else None
            })

        # Visits
        for visit in patient.visits:
            events.append({
                "type": "visit",
                "id": visit.id,
                "date": visit.visit_date.isoformat(),
                "title": f"Clinical Visit / Examination",
                "diagnosis": visit.diagnosis,
                "notes": visit.clinical_notes,
                "oral_findings": visit.oral_findings,
                "dentist": visit.dentist.user.full_name if visit.dentist and visit.dentist.user else None
            })

        # Prescriptions
        for rx in patient.prescriptions:
            events.append({
                "type": "prescription",
                "id": rx.id,
                "date": rx.created_at.date().isoformat(),
                "title": f"Prescription #{rx.prescription_number}",
                "item_count": len(rx.items),
                "dentist": rx.dentist.user.full_name if rx.dentist and rx.dentist.user else None
            })

        # Treatment Plans
        for tp in patient.treatment_plans:
            events.append({
                "type": "treatment_plan",
                "id": tp.id,
                "date": tp.created_at.date().isoformat(),
                "title": f"Treatment Plan: {tp.title}",
                "status": tp.status,
                "total": float(tp.estimated_total),
                "dentist": tp.dentist.user.full_name if tp.dentist and tp.dentist.user else None
            })

        # Invoices
        for inv in patient.invoices:
            events.append({
                "type": "invoice",
                "id": inv.id,
                "date": inv.issue_date.isoformat(),
                "title": f"Invoice #{inv.invoice_number}",
                "status": inv.status,
                "total": float(inv.total),
                "balance": float(inv.balance)
            })

        # Sort timeline descending by date
        events.sort(key=lambda x: x["date"], reverse=True)
        return events
