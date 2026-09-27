# Apex Dental Care - REST API Reference

Base URL: `/api/v1`  
OpenAPI Documentation: `http://localhost:8000/docs` or `http://localhost:8000/redoc`

---

## 1. Authentication Endpoints

| Method | Endpoint | Allowed Roles | Description | Status Code |
|---|---|---|---|---|
| `POST` | `/auth/login` | Public | Authenticate with username or email and password | `200 OK` |
| `POST` | `/auth/refresh` | Public | Exchange valid refresh token for a new access token | `200 OK` |
| `POST` | `/auth/logout` | Authenticated | Revoke refresh token and terminate active session | `200 OK` |
| `GET` | `/auth/me` | Authenticated | Retrieve currently authenticated user profile | `200 OK` |

---

## 2. Patients & Clinical Records

| Method | Endpoint | Allowed Roles | Description | Status Code |
|---|---|---|---|---|
| `GET` | `/patients` | Admin, Dentist, Receptionist | List patients with pagination, search, and sorting | `200 OK` |
| `POST` | `/patients` | Admin, Receptionist | Register a new patient and initialize 32 teeth | `201 Created` |
| `GET` | `/patients/{id}` | Admin, Dentist, Receptionist | Get comprehensive patient profile & medical history | `200 OK` |
| `PUT` | `/patients/{id}` | Admin, Receptionist | Update patient demographics & contact info | `200 OK` |
| `DELETE` | `/patients/{id}` | Admin | Soft-delete / archive patient record | `200 OK` |
| `GET` | `/patients/{id}/timeline` | Admin, Dentist, Receptionist | Get complete chronological clinical history timeline | `200 OK` |

---

## 3. FDI Dental Chart Endpoints

| Method | Endpoint | Allowed Roles | Description | Status Code |
|---|---|---|---|---|
| `GET` | `/dental-chart/patient/{patient_id}` | Admin, Dentist, Receptionist | Retrieve all 32 teeth conditions and historical notes | `200 OK` |
| `PUT` | `/dental-chart/patient/{patient_id}/tooth/{tooth_number}` | Admin, Dentist | Update tooth condition & append to clinical history | `200 OK` |
| `GET` | `/dental-chart/patient/{patient_id}/tooth/{tooth_number}/history` | Admin, Dentist | View detailed longitudinal history for single tooth | `200 OK` |

---

## 4. Appointments & Scheduling

| Method | Endpoint | Allowed Roles | Description | Status Code |
|---|---|---|---|---|
| `GET` | `/appointments` | Admin, Dentist, Receptionist | Query appointments by date, dentist, or status | `200 OK` |
| `POST` | `/appointments` | Admin, Receptionist | Book appointment with conflict & double-booking check | `201 Created` |
| `GET` | `/appointments/types` | Admin, Dentist, Receptionist | List standard appointment types and durations | `200 OK` |
| `GET` | `/appointments/{id}` | Admin, Dentist, Receptionist | Retrieve appointment details | `200 OK` |
| `PUT` | `/appointments/{id}` | Admin, Receptionist | Reschedule or edit appointment details | `200 OK` |
| `PATCH` | `/appointments/{id}/status` | Admin, Dentist, Receptionist | Transition status (`confirmed`, `completed`, `cancelled`) | `200 OK` |

---

## 5. Clinical Visits & Examinations

| Method | Endpoint | Allowed Roles | Description | Status Code |
|---|---|---|---|---|
| `POST` | `/visits` | Admin, Dentist | Record clinical visit, vitals, and examination findings | `201 Created` |
| `GET` | `/visits/{id}` | Admin, Dentist, Receptionist | Retrieve specific visit details and diagnoses | `200 OK` |
| `GET` | `/visits/patient/{patient_id}` | Admin, Dentist, Receptionist | List all clinical visits for a patient | `200 OK` |

---

## 6. Treatment Plans & Procedures

| Method | Endpoint | Allowed Roles | Description | Status Code |
|---|---|---|---|---|
| `GET` | `/treatments/catalog` | Admin, Dentist, Receptionist | Standard procedure fee catalog with CDT codes | `200 OK` |
| `GET` | `/treatments/plans` | Admin, Dentist, Receptionist | List treatment plans with patient/dentist filter | `200 OK` |
| `POST` | `/treatments/plans` | Admin, Dentist | Create multi-procedure treatment plan | `201 Created` |
| `GET` | `/treatments/plans/{id}` | Admin, Dentist, Receptionist | Get treatment plan details and item progress | `200 OK` |
| `POST` | `/treatments/plans/{id}/items`| Admin, Dentist | Add new procedure item to existing plan | `200 OK` |
| `PUT` | `/treatments/items/{item_id}` | Admin, Dentist | Update procedure status (`in_progress`, `completed`) | `200 OK` |

---

## 7. Prescriptions & Official PDF

| Method | Endpoint | Allowed Roles | Description | Status Code |
|---|---|---|---|---|
| `GET` | `/prescriptions/catalog` | Admin, Dentist | Approved pharmacy formulary & medications | `200 OK` |
| `GET` | `/prescriptions` | Admin, Dentist | List issued prescriptions | `200 OK` |
| `POST` | `/prescriptions` | Admin, Dentist | Create new multi-item prescription | `201 Created` |
| `GET` | `/prescriptions/{id}` | Admin, Dentist | Retrieve prescription record and items | `200 OK` |
| `GET` | `/prescriptions/{id}/pdf` | Admin, Dentist | Stream vector PDF with digital clinic letterhead | `200 OK` |

---

## 8. Billing, Payments & Invoices

| Method | Endpoint | Allowed Roles | Description | Status Code |
|---|---|---|---|---|
| `GET` | `/billing/invoices` | Admin, Receptionist | List invoices with status & balance filters | `200 OK` |
| `POST` | `/billing/invoices` | Admin, Receptionist | Create itemized patient invoice | `201 Created` |
| `GET` | `/billing/invoices/{id}` | Admin, Receptionist | Get full invoice details, line items, and payments | `200 OK` |
| `GET` | `/billing/invoices/{id}/pdf` | Admin, Receptionist | Stream printable invoice PDF | `200 OK` |
| `POST` | `/billing/payments` | Admin, Receptionist | Record transactional payment with atomic balance update | `201 Created` |

---

## 9. Documents & Diagnostic X-Rays

| Method | Endpoint | Allowed Roles | Description | Status Code |
|---|---|---|---|---|
| `GET` | `/documents` | Admin, Dentist, Receptionist | List clinic archived documents & images | `200 OK` |
| `POST` | `/documents/upload` | Admin, Dentist, Receptionist | Secure multipart upload for X-rays and reports | `201 Created` |
| `GET` | `/documents/patient/{patient_id}`| Admin, Dentist, Receptionist | List all files belonging to a patient | `200 OK` |
| `GET` | `/documents/{id}/download` | Admin, Dentist, Receptionist | Stream authorized document with audit record | `200 OK` |

---

## 10. Reports, Compliance & System Health

| Method | Endpoint | Allowed Roles | Description | Status Code |
|---|---|---|---|---|
| `GET` | `/reports/revenue` | Admin, Receptionist | Payment receipts and revenue ledger with date filters | `200 OK` |
| `GET` | `/reports/revenue/export-csv`| Admin, Receptionist | Export revenue ledger as CSV file | `200 OK` |
| `GET` | `/reports/outstanding` | Admin, Receptionist | Unsettled patient receivables report | `200 OK` |
| `GET` | `/audit-logs` | Admin | Searchable audit trail of mutating events | `200 OK` |
| `GET` | `/health` | Public | Liveness probe returning application state | `200 OK` |
| `GET` | `/health/ready` | Public | Readiness probe verifying database connection | `200 OK` |

---

## 11. Error Response Format

All error responses return a standardized, non-leaking JSON envelope:

```json
{
  "error": {
    "code": "APPOINTMENT_CONFLICT",
    "message": "The selected dentist already has a conflicting appointment at this time.",
    "details": {
      "dentist_id": 2,
      "conflicting_time": "10:00:00"
    }
  }
}
```
