from app.schemas.common import ErrorResponse, ErrorDetail, PaginatedResponse, MessageResponse
from app.schemas.auth import LoginRequest, TokenResponse, RefreshTokenRequest, PasswordChangeRequest
from app.schemas.user import UserCreate, UserUpdate, UserResponse, DentistProfileCreate, DentistProfileResponse
from app.schemas.patient import (
    PatientCreate, PatientUpdate, PatientListItem, PatientDetailResponse,
    MedicalHistoryBase, MedicalHistoryResponse, DentalHistoryBase, DentalHistoryResponse
)
from app.schemas.appointment import (
    AppointmentCreate, AppointmentUpdate, AppointmentStatusUpdate, AppointmentResponse, AppointmentTypeResponse
)
from app.schemas.clinical import VisitCreate, VisitUpdate, VisitResponse
from app.schemas.dental_chart import (
    ToothConditionUpdate, ToothConditionResponse, ToothHistoryResponse, DentalChartDetailResponse
)
from app.schemas.treatment import (
    TreatmentPlanCreate, TreatmentPlanUpdate, TreatmentPlanResponse,
    TreatmentItemCreate, TreatmentItemUpdate, TreatmentItemResponse, ProcedureCatalogResponse
)
from app.schemas.prescription import (
    PrescriptionCreate, PrescriptionResponse, PrescriptionItemCreate, PrescriptionItemResponse, MedicineCatalogResponse
)
from app.schemas.billing import (
    InvoiceCreate, InvoiceResponse, InvoiceItemCreate, InvoiceItemResponse,
    PaymentCreate, PaymentResponse
)
from app.schemas.document import DocumentResponse, DocumentUpdate
from app.schemas.followup import FollowUpCreate, FollowUpUpdate, FollowUpResponse
from app.schemas.dashboard import DashboardSummaryResponse, DashboardAnalyticsResponse
from app.schemas.audit import AuditLogResponse
