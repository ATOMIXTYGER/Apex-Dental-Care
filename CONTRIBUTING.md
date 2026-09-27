# Contributing to Apex Dental Care

Thank you for your interest in contributing to Apex Dental Care. As a healthcare software platform handling sensitive patient records, all code contributions must satisfy strict security, test coverage, and design standards.

---

## 1. Development Principles

1. **Defense in Depth:** Never trust client-side validation alone. Every endpoint must enforce server-side validation and authorization.
2. **Clinical Safety Boundary:** The platform is a clinical record and management system. Autonomous medical or dental diagnosis without clinician oversight is strictly out of scope.
3. **Financial Precision:** Currency calculations must always use `Decimal` and SQL `Numeric(10, 2)`.
4. **Zero Regressions:** Every PR must include corresponding automated tests (Pytest for backend, Vitest for frontend, or Playwright for workflows).

---

## 2. Coding Standards

### Backend (Python / FastAPI)
- Formatted and linted using `ruff`:
  ```bash
  cd backend
  ruff check .
  ruff format .
  ```
- All schema models must use Pydantic v2 conventions (`model_config = ConfigDict(from_attributes=True)`).
- ORM entities must inherit from `Base` with explicit indexes and foreign key cascades.

### Frontend (React / TypeScript)
- Strict mode enabled (`strict: true`).
- Formatted with Prettier and Tailwind CSS class order.
- Verify TypeScript types without emitting:
  ```bash
  cd frontend
  npm run lint
  ```

---

## 3. Pull Request Checklist

Before submitting a PR, verify:
- [ ] Backend tests pass: `pytest -v` (in `backend/`)
- [ ] Frontend tests pass: `npm test` (in `frontend/`)
- [ ] Frontend builds cleanly: `npm run build` (in `frontend/`)
- [ ] No secrets, keys, or passwords committed.
- [ ] Database schema changes include an Alembic migration (`alembic revision --autogenerate`).
- [ ] Centralized audit logging is added for new mutating operations.
