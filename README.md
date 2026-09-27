# Apex Dental Care - Smart Dental Clinic Management & Patient Record System

[![CI/CD Pipeline](https://github.com/apex-dental/clinic-system/actions/workflows/ci.yml/badge.svg)](https://github.com/apex-dental/clinic-system/actions)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3-61dafb.svg?logo=react)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178c6.svg?logo=typescript)](https://www.typescriptlang.org)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-d71f00.svg)](https://www.sqlalchemy.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Apex Dental Care is a **production-ready, end-to-end dental clinic management and electronic dental record (EDR) platform**. Designed for high-volume dental practices, hospital dental wings, and solo practices, the system replaces paper charts and disjointed software with a unified, HIPAA-aware clinical workflow.

---

## 🌟 Key Features & Clinical Capabilities

1. **FDI Two-Digit World Dental Federation Charting (11–48):**
   - Full anatomical 32-tooth permanent dentition covering all 4 quadrants (Maxilla & Mandible).
   - Multi-surface condition tracking (Mesial, Distal, Occlusal, Buccal, Lingual).
   - Clinical statuses: Healthy, Caries, Filled, Crown, Root Canal, Missing, Extraction, Fracture, Sensitivity, Mobility, Bridge, Implant.
   - Preserves complete immutable clinical tooth history across visits.

2. **Patient Registration & Longitudinal 10-Tab Clinical Dossier:**
   - Demographics, emergency contacts, medical alerts, allergy tracking, current medications.
   - Tabbed records: Overview, Medical History, Clinical Visits, FDI Tooth Chart, Treatment Plans, Prescriptions, Documents & X-rays, Invoices & Payments, Follow-ups, and Audit History.

3. **Conflict-Free Appointment Scheduling:**
   - Multi-dentist calendar schedule with operatory allocation.
   - Real-time double-booking prevention engine at service and database level.
   - Status transitions: `scheduled` → `confirmed` → `completed` / `cancelled` / `no_show`.

4. **Clinical Examination & Diagnosis Workflow:**
   - Vital signs recording (Blood Pressure, Heart Rate).
   - Periodontal gum assessment, plaque/calculus hygiene indices, chief complaints, and oral findings.
   - Direct linking between Appointments, Visits, and Tooth Conditions.

5. **Multi-Procedure Treatment Plans:**
   - Multi-stage phased treatment plans with procedure itemization.
   - Procedure Fee Catalog with standardized dental procedure codes (CDT-compatible).
   - Progress tracking: `planned` → `in_progress` → `completed`.
   - Python `Decimal` and SQLAlchemy `Numeric(10, 2)` calculations (zero floating-point currency drift).

6. **Prescriptions & Official PDF Generation:**
   - Dental pharmacy formulary integration (Amoxicillin, Clindamycin, Ibuprofen, Chlorhexidine, etc.).
   - Medicine dosage, frequency, duration, route, and timing instructions.
   - Official signed vector PDF generated on-the-fly via ReportLab with security disclaimers and clinic letterhead.

7. **Transactional Billing, Payments & Invoices:**
   - Itemized invoices with item description, unit price, quantity, tax, and discounts.
   - Payment recording supporting Cash, Credit Card, UPI, and Bank Transfers.
   - Atomic balance tracking (`balance = total - sum(payments)`).
   - Printable official tax invoices generated via ReportLab.

8. **Secure Document & X-Ray Vault:**
   - Storage abstraction for Panoramic OPGs, IOPA X-rays, CBCT scans, lab reports, and signed consent forms.
   - Path traversal guards, MIME-type and file extension validation, randomized server-side UUID filenames.
   - Protected download endpoints enforcing strict role-based access control.

9. **Centralized Compliance & Audit Logging:**
   - Immutable audit trail recording user, action, target entity, timestamp, IP address, and client headers.
   - Recursive metadata sanitization (passwords, JWTs, and keys are automatically scrubbed).
   - Admin-only filterable audit inspection viewer.

10. **Database-Driven Dashboard & Analytics:**
    - Live KPIs: Total Patients, Appointments Today, Pending Treatments, Revenue Collected, Outstanding Receivables, Follow-ups Due.
    - Recharts visual analytics: Revenue stream trends, appointment status distributions, and procedure volume charts.

---

## 🏗️ Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS, TanStack Query v5, React Router v6, Lucide Icons, Recharts |
| **Backend** | Python 3.11/3.13, FastAPI, Pydantic v2 (`ConfigDict`), SQLAlchemy 2.x, Alembic |
| **Database** | MySQL 8.0 (Production) / SQLite with Decimal precision (Local Dev/Testing) |
| **Authentication** | JWT Access Tokens + HTTP-only SHA-256 Refresh Token Rotation, Bcrypt password hashing |
| **Document Engine** | ReportLab 4.x (Prescription & Invoice PDF Generation) |
| **Infrastructure** | Docker, Docker Compose, Nginx (Alpine), Multi-stage builds |
| **Testing** | Pytest, Pytest-Asyncio, HTTPX, Vitest, React Testing Library, Playwright E2E |

---

## 🚀 Quick Start with Docker

The entire platform (MySQL 8, FastAPI backend, and Nginx React frontend) can be spun up with one command:

```bash
# 1. Clone repository
git clone https://github.com/apex-dental/clinic-system.git
cd clinic-system

# 2. Start all services via Docker Compose
docker compose up --build
```

Once started:
- **Web Application Portal:** [http://localhost:3000](http://localhost:3000)
- **FastAPI OpenAPI Swagger Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **FastAPI Health Endpoint:** [http://localhost:8000/api/v1/health/ready](http://localhost:8000/api/v1/health/ready)

---

## 💻 Local Development Setup

### 1. Backend Setup

```bash
cd backend

# Create and activate python virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Seed realistic demo database
python seeds/seed_data.py

# Launch development server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Launch Vite development server
npm run dev
```

Frontend will run at [http://localhost:3000](http://localhost:3000) with automatic hot-module reloading and API proxying to port 8000.

---

## 🔑 Demo User Credentials

The database seeder pre-populates the platform with realistic clinical records and staff accounts:

| Role | Email | Password | Full Name & Title |
|---|---|---|---|
| **Administrator** | `admin@clinic.com` | `Dental@123` | Dr. Sarah Jenkins (Chief Medical Officer) |
| **Dentist** | `dr.chen@clinic.com` | `Dental@123` | Dr. Marcus Chen (Periodontist, Operatory 1) |
| **Dentist** | `dr.alvarez@clinic.com` | `Dental@123` | Dr. Elena Alvarez (Prosthodontist, Operatory 2) |
| **Receptionist** | `reception1@clinic.com` | `Dental@123` | Jessica Miller (Head Front Desk Coordinator) |
| **Receptionist** | `reception2@clinic.com` | `Dental@123` | David Ross (Patient Care Coordinator) |

> ⚠️ **Security Notice:** The above credentials are provided exclusively for evaluation and demo environments. Production environments must change all passwords and rotate JWT secrets immediately upon initialization.

---

## 🧪 Testing Suites

### Backend Tests (29 automated tests)
```bash
cd backend
venv\Scripts\pytest -v
```

### Frontend Tests (Vitest + React Testing Library)
```bash
cd frontend
npm test
```

### End-to-End Tests (Playwright)
```bash
cd e2e
npx playwright test
```

---

## 📁 Repository Structure

```
├── backend/
│   ├── alembic/                # Database migration scripts
│   ├── app/
│   │   ├── audit/              # Centralized audit logger & payload sanitizer
│   │   ├── models/             # SQLAlchemy 2.0 ORM entity models
│   │   ├── pdf/                # ReportLab vector PDF generators
│   │   ├── routers/            # FastAPI REST endpoints
│   │   ├── schemas/            # Pydantic v2 schemas
│   │   ├── security/           # JWT, Bcrypt, and RBAC permissions matrix
│   │   ├── services/           # Business logic service layer
│   │   ├── storage/            # Secure local/S3 file storage abstraction
│   │   ├── config.py           # Pydantic Settings configuration
│   │   ├── database.py         # SQLAlchemy engine & session management
│   │   └── main.py             # FastAPI application entrypoint & middlewares
│   ├── seeds/                  # Realistic clinical demo seeder
│   ├── tests/                  # Pytest automated test suites
│   ├── Dockerfile              # Backend container build
│   └── requirements.txt        # Python dependency manifest
├── frontend/
│   ├── src/
│   │   ├── api/                # Axios/Fetch typed REST API clients
│   │   ├── components/         # Modals, layout, and FDI tooth chart
│   │   ├── context/            # AuthContext & Session management
│   │   ├── pages/              # 10 primary module views
│   │   ├── test/               # Vitest component & RBAC test specs
│   │   ├── types/              # Comprehensive TypeScript interfaces
│   │   ├── App.tsx             # React Router v6 & QueryClient configuration
│   │   └── main.tsx            # DOM root entrypoint
│   ├── nginx.conf              # Production Nginx reverse proxy configuration
│   ├── Dockerfile              # Multi-stage frontend container build
│   └── package.json            # Node.js dependencies
├── e2e/                        # Playwright E2E test workflows
├── .github/workflows/ci.yml    # Full GitHub Actions CI/CD pipeline
├── docker-compose.yml          # Multi-container orchestration
└── .env.example                # Environment variable configuration template
```

---

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
