from enum import StrEnum


class Role(StrEnum):
    ADMIN = "admin"
    DENTIST = "dentist"
    RECEPTIONIST = "receptionist"
    PATIENT = "patient"

# Specific permission strings
class Permission(StrEnum):
    # User / System
    USER_MANAGE = "user:manage"
    SYSTEM_CONFIG = "system:config"
    AUDIT_VIEW = "audit:view"

    # Patient
    PATIENT_READ = "patient:read"
    PATIENT_CREATE = "patient:create"
    PATIENT_UPDATE = "patient:update"
    PATIENT_DELETE = "patient:delete"

    # Clinical
    CLINICAL_READ = "clinical:read"
    CLINICAL_CREATE = "clinical:create"
    CLINICAL_UPDATE = "clinical:update"

    # Dental Chart
    CHART_READ = "chart:read"
    CHART_UPDATE = "chart:update"

    # Treatment
    TREATMENT_READ = "treatment:read"
    TREATMENT_MANAGE = "treatment:manage"

    # Prescription
    PRESCRIPTION_READ = "prescription:read"
    PRESCRIPTION_CREATE = "prescription:create"

    # Appointments
    APPOINTMENT_READ = "appointment:read"
    APPOINTMENT_MANAGE = "appointment:manage"

    # Billing
    BILLING_READ = "billing:read"
    BILLING_MANAGE = "billing:manage"

    # Documents
    DOCUMENT_READ = "document:read"
    DOCUMENT_UPLOAD = "document:upload"
    DOCUMENT_DELETE = "document:delete"

ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.ADMIN: {
        Permission.USER_MANAGE,
        Permission.SYSTEM_CONFIG,
        Permission.AUDIT_VIEW,
        Permission.PATIENT_READ,
        Permission.PATIENT_CREATE,
        Permission.PATIENT_UPDATE,
        Permission.PATIENT_DELETE,
        Permission.CLINICAL_READ,
        Permission.CHART_READ,
        Permission.TREATMENT_READ,
        Permission.PRESCRIPTION_READ,
        Permission.APPOINTMENT_READ,
        Permission.APPOINTMENT_MANAGE,
        Permission.BILLING_READ,
        Permission.BILLING_MANAGE,
        Permission.DOCUMENT_READ,
        Permission.DOCUMENT_DELETE,
    },
    Role.DENTIST: {
        Permission.PATIENT_READ,
        Permission.CLINICAL_READ,
        Permission.CLINICAL_CREATE,
        Permission.CLINICAL_UPDATE,
        Permission.CHART_READ,
        Permission.CHART_UPDATE,
        Permission.TREATMENT_READ,
        Permission.TREATMENT_MANAGE,
        Permission.PRESCRIPTION_READ,
        Permission.PRESCRIPTION_CREATE,
        Permission.APPOINTMENT_READ,
        Permission.APPOINTMENT_MANAGE,
        Permission.BILLING_READ,
        Permission.DOCUMENT_READ,
        Permission.DOCUMENT_UPLOAD,
    },
    Role.RECEPTIONIST: {
        Permission.PATIENT_READ,
        Permission.PATIENT_CREATE,
        Permission.PATIENT_UPDATE,
        Permission.APPOINTMENT_READ,
        Permission.APPOINTMENT_MANAGE,
        Permission.BILLING_READ,
        Permission.BILLING_MANAGE,
        Permission.DOCUMENT_READ,
        Permission.DOCUMENT_UPLOAD,
    },
    Role.PATIENT: {
        Permission.PATIENT_READ,
        Permission.APPOINTMENT_READ,
        Permission.BILLING_READ,
        Permission.DOCUMENT_READ,
    }
}
