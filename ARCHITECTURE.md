# Apex Dental Care - System Architecture Document

## 1. Architectural Philosophy & Overview

Apex Dental Care is architected as a **stateless, micro-service ready, modular monolith**. The system decouples presentation, orchestration, and persistence into clear architectural layers, ensuring that business logic is strictly isolated from HTTP delivery protocols.

```mermaid
graph TD
    Client["React 18 SPA (Vite + TypeScript)"]
    Nginx["Nginx Reverse Proxy & Static Host"]
    FastAPI["FastAPI REST Application Layer"]
    Middlewares["Security Headers & Correlation Middlewares"]
    Routers["REST Routers (/patients, /treatments, etc.)"]
    Services["Service Layer (Business Rules & Validation)"]
    ORM["SQLAlchemy 2.0 ORM Mappings"]
    Database[("MySQL 8.0 / Relational DB")]
    FileVault[("Secure File Storage Vault")]
    PDFEngine["ReportLab Vector PDF Engine"]
    AuditService["Centralized Audit Logger"]

    Client -->|HTTPS / API Requests| Nginx
    Nginx -->|Proxy Pass| FastAPI
    FastAPI --> Middlewares
    Middlewares --> Routers
    Routers --> Services
    Services --> ORM
    Services --> PDFEngine
    Services --> FileVault
    Services --> AuditService
    ORM --> Database
    AuditService --> Database
```

---

## 2. Layered Backend Design

The backend enforces strict separation of concerns across 5 distinct tiers:

### 1. Delivery Tier (`app/routers/`)
- Pure HTTP handling: Parameter deserialization, request schema validation, status code assignment, and content negotiation.
- Implements dependency injection for user authentication (`get_current_user`) and RBAC verification (`require_roles`).
- Zero direct database mutations or business calculations occur within routers.

### 2. Service Tier (`app/services/`)
- Contains 100% of domain business logic.
- Atomic business transactions, conflict detection (e.g. appointment double-booking), financial aggregations, and tooth condition history creation.
- Explicit transactional scope management with automated rollbacks on failure.

### 3. Model & Persistence Tier (`app/models/` & `app/database.py`)
- Declarative SQLAlchemy 2.0 ORM entity definitions.
- Explicit foreign keys, unique composite indexes, soft-delete flags (`is_deleted`), and timestamp tracking (`created_at`, `updated_at`).
- All currency columns defined as `Numeric(10, 2)` to eliminate floating-point arithmetic errors.

### 4. Security Tier (`app/security/`)
- Cryptographic password hashing using standard Argon2id / Bcrypt implementations.
- JWT access token minting and cryptographic verification.
- Cryptographically random refresh token generation with SHA-256 hash storage in the database.
- Declarative role-permission matrix.

### 5. Cross-Cutting Utilities (`app/audit/`, `app/pdf/`, `app/storage/`)
- **Centralized Audit Logger:** Automatically captures mutating events with recursive sensitive-data sanitization.
- **ReportLab PDF Generator:** Generates compliant vector PDF documents with clinic branding.
- **Storage Abstraction:** Protects uploads with UUID renaming, MIME verification, and path traversal guards.

---

## 3. Frontend Architecture

The frontend is built on React 18, TypeScript, and Vite, prioritizing predictable state management and minimal re-renders:

```mermaid
graph LR
    subgraph UI Components
        Pages["Pages (e.g. PatientDetail.tsx)"]
        Components["Feature Modals & Components"]
        Chart["FDI Anatomical SVG Chart (11-48)"]
    end

    subgraph State Management
        Auth["AuthContext (JWT & Current User)"]
        Query["TanStack Query Cache (Server State)"]
        Forms["React Hook Form + Zod (Form State)"]
    end

    subgraph Network Layer
        ApiClient["Axios / Fetch Client (/api/v1)"]
        Interceptors["Auth Interceptor (Bearer Token & 401 Refresh)"]
    end

    Pages --> Components
    Components --> Chart
    Components --> Forms
    Pages --> Query
    Pages --> Auth
    Query --> ApiClient
    ApiClient --> Interceptors
```

### Server State vs Local UI State
- **Server State:** Managed exclusively through `@tanstack/react-query` with declarative query keys (e.g. `['patient', id]`, `['treatmentPlans', status]`). Mutations invalidate corresponding cache keys to trigger re-renders without manual state synchronization.
- **Form State:** Managed with controlled inputs and strict validation schemas.
- **Global Context:** Reserved strictly for authentication session tokens and active user profile.

---

## 4. Clinical Workflow Sequences

### Appointment & Examination Lifecycle

```mermaid
sequenceDiagram
    autonumber
    actor Receptionist
    actor Dentist
    participant ApptService as Appointment Service
    participant VisitService as Clinical Visit Service
    participant DentalService as FDI Dental Chart Service
    participant DB as Relational Database

    Receptionist->>ApptService: Book Appointment (patient_id, dentist_id, date, start_time)
    ApptService->>DB: Query Overlapping Appointments for Dentist
    alt Conflict Exists
        ApptService-->>Receptionist: 409 Conflict Error
    else Slot Available
        ApptService->>DB: Insert Appointment (status='scheduled')
        ApptService-->>Receptionist: Appointment Confirmed
    end

    Dentist->>VisitService: Start Visit (appointment_id, patient_id)
    VisitService->>DB: Insert Visit & Update Appointment status='completed'
    Dentist->>DentalService: Update Tooth 16 Condition (condition='caries', severity='moderate')
    DentalService->>DB: Update Current Tooth 16 & Insert Tooth History Record
    DentalService-->>Dentist: Updated Tooth Chart State
```

---

## 5. Security & Isolation Boundaries

1. **Network Boundary:** The database (`apex_dental_mysql`) is placed in an internal Docker network and is inaccessible from the public internet.
2. **Access Boundary:** Reverse proxy (Nginx) terminates external HTTP requests and applies security headers before forwarding traffic to the application server.
3. **Application Boundary:** Every sensitive route verifies both authentication (valid JWT signature and unexpired token) and authorization (user's role matches required endpoint permission).
