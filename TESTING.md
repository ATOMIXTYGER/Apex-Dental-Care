# Apex Dental Care - Quality Assurance & Testing Strategy

Apex Dental Care employs a comprehensive, multi-tiered testing strategy covering unit logic, database integrations, security vulnerabilities, component rendering, and end-to-end browser workflows.

```
       /\
      /  \     End-to-End Tests (Playwright)
     /----\    4 Complete Critical Clinical Workflows
    /      \
   /--------\   Integration & Security Tests (Pytest + HTTPX)
  /          \  RBAC, IDOR, Injection, Double-Booking, Auth
 /------------\
/   Unit Tests \ Unit Logic (Bcrypt, Decimal Math, FDI 11-48, ReportLab)
----------------
```

---

## 1. Automated Test Suites Summary

| Test Suite | Framework | Scope / Components Tested |
|---|---|---|
| **Backend Unit & Integration** | Pytest + HTTPX | Authentication, token rotation, patient CRUD, appointment conflict detection, tooth condition history, treatment plans, prescriptions, invoices, and payments. |
| **Backend Security & RBAC** | Pytest | Role boundary enforcement, receptionist denied clinical edits, dentist denied admin operations, IDOR attempts, SQL injection payloads, XSS rejection, path traversal in uploads. |
| **Frontend Unit & Components** | Vitest + React Testing Library | FDI Dental Chart 32 permanent teeth rendering, color mapping, quadrant layout, ProtectedRoute role gates, AuthContext lifecycle. |
| **End-to-End (E2E)** | Playwright | 4 complete user workflows spanning Receptionist, Dentist, and Administrator personas. |

---

## 2. Executing Backend Tests

The backend test suite executes 29 comprehensive test cases against an in-memory test database populated with identical schema migrations and seed fixtures.

```bash
cd backend
venv\Scripts\activate

# Run full test suite with verbose output
pytest -v

# Run with test coverage report
pytest --cov=app --cov-report=term-missing
```

### Key Security & Clinical Test Cases Tested:
- `test_login_success_and_jwt_issuance`: Verifies Argon2/Bcrypt password validation and JWT token claims.
- `test_failed_login_and_account_lockout`: Confirms account locking after 5 consecutive bad passwords.
- `test_appointment_conflict_detection`: Ensures two patients cannot book the same dentist during overlapping hours.
- `test_fdi_permanent_teeth_initialization`: Verifies all 32 teeth (11-48) are generated with valid FDI numbering.
- `test_fdi_invalid_tooth_number`: Rejects out-of-range teeth (e.g. Tooth 99) with HTTP 422.
- `test_tooth_condition_history_preservation`: Ensures updating a tooth preserves complete historical logs.
- `test_treatment_plan_calculations`: Confirms exact monetary sums without floating-point errors.
- `test_receptionist_cannot_create_prescription`: Confirms HTTP 403 Forbidden when front-desk attempts clinical prescribing.
- `test_receptionist_cannot_modify_dental_chart`: Confirms HTTP 403 when front-desk attempts tooth condition modification.
- `test_dentist_cannot_manage_users`: Confirms HTTP 403 when clinicians attempt administrative user creation.
- `test_sql_injection_payloads_in_search`: Ensures malicious SQL `' OR '1'='1` cannot bypass parameterized queries.
- `test_path_traversal_prevention_in_uploads`: Verifies filenames like `../../etc/passwd` are safely renamed to UUIDs.

---

## 3. Executing Frontend Tests

Frontend tests verify component state, anatomical SVG tooth charting, and client-side route access control.

```bash
cd frontend

# Run Vitest test runner
npm test

# Run tests in watch mode
npx vitest
```

---

## 4. Executing End-to-End (E2E) Browser Tests

Playwright tests execute the 4 mandatory production workflows in headless or headed Chromium:

```bash
# Ensure backend and frontend are running or run via docker-compose
docker compose up -d

# Run Playwright test suite
cd e2e
npx playwright test

# View interactive HTML test report
npx playwright show-report
```

### The 4 Workflows Verified:
1. **Workflow 1 (Receptionist):** Login → Patient Registration → Schedule Appointment.
2. **Workflow 2 (Dentist):** Login → Examination → FDI Dental Chart Update → Treatment Plan → Prescription PDF.
3. **Workflow 3 (Receptionist):** Invoice Inspection → Record Payment → Verify Balance Reduction.
4. **Workflow 4 (Administrator):** Login → Centralized Audit Logs Review → Staff & User Management.
