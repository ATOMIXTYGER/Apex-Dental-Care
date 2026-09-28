from datetime import date, time

from fastapi import HTTPException, Request, status
from sqlalchemy.orm import Session

from app.audit.service import log_audit_event
from app.models.appointment import Appointment
from app.models.patient import Patient
from app.models.user import Dentist, User
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentStatusUpdate,
    AppointmentUpdate,
)


class AppointmentService:
    @staticmethod
    def check_conflict(
        db: Session,
        dentist_id: int,
        appointment_date: date,
        start_time: time,
        end_time: time,
        exclude_id: int | None = None
    ) -> bool:
        """
        Check if the dentist has any active overlapping appointment.
        Overlaps if (start_time < existing.end_time) and (end_time > existing.start_time).
        """
        query = db.query(Appointment).filter(
            Appointment.dentist_id == dentist_id,
            Appointment.appointment_date == appointment_date,
            Appointment.status.notin_(["cancelled", "no_show"]),
            Appointment.start_time < end_time,
            Appointment.end_time > start_time
        )
        if exclude_id:
            query = query.filter(Appointment.id != exclude_id)

        return query.first() is not None

    @classmethod
    def create_appointment(
        cls,
        db: Session,
        data: AppointmentCreate,
        current_user: User,
        request: Request | None = None
    ) -> Appointment:
        """Create a new appointment with strict validation and conflict prevention."""
        # Validate patient
        patient = db.query(Patient).filter(Patient.id == data.patient_id, Patient.is_deleted == False).first()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "PATIENT_NOT_FOUND", "message": "Patient does not exist."}
            )

        # Validate dentist
        dentist = db.query(Dentist).filter(Dentist.id == data.dentist_id, Dentist.is_active == True).first()
        if not dentist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "DENTIST_NOT_FOUND", "message": "Dentist does not exist or is inactive."}
            )

        # Validate time logic
        if data.start_time >= data.end_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "INVALID_TIME_RANGE", "message": "Appointment end time must be after start time."}
            )

        # Check dentist conflict
        if cls.check_conflict(db, data.dentist_id, data.appointment_date, data.start_time, data.end_time):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "APPOINTMENT_CONFLICT",
                    "message": "The selected dentist already has a conflicting appointment at this date and time."
                }
            )

        appointment = Appointment(
            patient_id=data.patient_id,
            dentist_id=data.dentist_id,
            appointment_type_id=data.appointment_type_id,
            appointment_date=data.appointment_date,
            start_time=data.start_time,
            end_time=data.end_time,
            status="scheduled",
            reason=data.reason,
            notes=data.notes
        )
        db.add(appointment)
        db.commit()
        db.refresh(appointment)

        log_audit_event(
            db=db,
            action="CREATE",
            user=current_user,
            entity_name="Appointment",
            entity_id=str(appointment.id),
            details={"patient_id": data.patient_id, "dentist_id": data.dentist_id, "date": str(data.appointment_date)},
            request=request
        )

        return appointment

    @staticmethod
    def get_appointments(
        db: Session,
        appointment_date: date | None = None,
        dentist_id: int | None = None,
        patient_id: int | None = None,
        status: str | None = None
    ) -> list[Appointment]:
        """Fetch appointments with optional date, dentist, patient, and status filters."""
        query = db.query(Appointment)
        if appointment_date:
            query = query.filter(Appointment.appointment_date == appointment_date)
        if dentist_id:
            query = query.filter(Appointment.dentist_id == dentist_id)
        if patient_id:
            query = query.filter(Appointment.patient_id == patient_id)
        if status:
            query = query.filter(Appointment.status == status)

        return query.order_by(Appointment.appointment_date.asc(), Appointment.start_time.asc()).all()

    @staticmethod
    def get_appointment_by_id(db: Session, appointment_id: int) -> Appointment:
        appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "APPOINTMENT_NOT_FOUND", "message": f"Appointment with ID {appointment_id} does not exist."}
            )
        return appt

    @classmethod
    def update_appointment(
        cls,
        db: Session,
        appointment_id: int,
        data: AppointmentUpdate,
        current_user: User,
        request: Request | None = None
    ) -> Appointment:
        """Update appointment details or reschedule with conflict validation."""
        appt = cls.get_appointment_by_id(db, appointment_id)

        target_dentist = data.dentist_id or appt.dentist_id
        target_date = data.appointment_date or appt.appointment_date
        target_start = data.start_time or appt.start_time
        target_end = data.end_time or appt.end_time

        if target_start >= target_end:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "INVALID_TIME_RANGE", "message": "Appointment end time must be after start time."}
            )

        if cls.check_conflict(db, target_dentist, target_date, target_start, target_end, exclude_id=appt.id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"code": "APPOINTMENT_CONFLICT", "message": "Rescheduling causes a conflict with another appointment."}
            )

        update_dict = data.model_dump(exclude_unset=True)
        for k, v in update_dict.items():
            setattr(appt, k, v)

        db.commit()
        db.refresh(appt)

        log_audit_event(
            db=db,
            action="UPDATE",
            user=current_user,
            entity_name="Appointment",
            entity_id=str(appt.id),
            details={"changes": list(update_dict.keys())},
            request=request
        )

        return appt

    @classmethod
    def update_status(
        cls,
        db: Session,
        appointment_id: int,
        data: AppointmentStatusUpdate,
        current_user: User,
        request: Request | None = None
    ) -> Appointment:
        """Transition status of an appointment (e.g. confirm, cancel, complete, no-show)."""
        appt = cls.get_appointment_by_id(db, appointment_id)
        appt.status = data.status
        if data.cancellation_reason:
            appt.cancellation_reason = data.cancellation_reason

        db.commit()
        db.refresh(appt)

        log_audit_event(
            db=db,
            action="STATUS_CHANGE",
            user=current_user,
            entity_name="Appointment",
            entity_id=str(appt.id),
            details={"new_status": data.status, "reason": data.cancellation_reason},
            request=request
        )

        return appt
