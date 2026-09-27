import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError

from app.config import settings
from app.database import engine, Base
# Import all models to register with Base
import app.models # noqa: F401

# Middlewares & Handlers
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.middleware.audit_middleware import RequestCorrelationMiddleware
from app.middleware.error_handler import (
    http_exception_handler, validation_exception_handler, unhandled_exception_handler
)

# Routers
from app.routers import (
    auth, users, patients, appointments, visits, dental_chart,
    treatments, prescriptions, documents, billing, followups,
    dashboard, reports, audit, health
)

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("dental_app")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables exist
    logger.info(f"Starting {settings.APP_NAME} in {settings.ENVIRONMENT} mode...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database schemas verified.")
    yield
    # Shutdown
    logger.info("Application shutting down...")

app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Smart Dental Clinic Management and Patient Record System.\n"
        "Production-grade RESTful API supporting clinical workflows, FDI tooth charting, "
        "role-based access control, appointment conflict prevention, digital prescriptions, "
        "ReportLab PDF generation, and centralized audit logging."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 1. Custom Error Handlers
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

# 2. Middlewares (Order: outermost executed first)
app.add_middleware(RequestCorrelationMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Response-Time", "Content-Disposition"]
)

# 3. Mount Routers under API prefix
api_prefix = settings.API_PREFIX # /api/v1
app.include_router(auth.router, prefix=api_prefix)
app.include_router(users.router, prefix=api_prefix)
app.include_router(patients.router, prefix=api_prefix)
app.include_router(appointments.router, prefix=api_prefix)
app.include_router(visits.router, prefix=api_prefix)
app.include_router(dental_chart.router, prefix=api_prefix)
app.include_router(treatments.router, prefix=api_prefix)
app.include_router(prescriptions.router, prefix=api_prefix)
app.include_router(documents.router, prefix=api_prefix)
app.include_router(billing.router, prefix=api_prefix)
app.include_router(followups.router, prefix=api_prefix)
app.include_router(dashboard.router, prefix=api_prefix)
app.include_router(reports.router, prefix=api_prefix)
app.include_router(audit.router, prefix=api_prefix)

# Health routes are accessible both root and under api_prefix
app.include_router(health.router)
app.include_router(health.router, prefix=api_prefix)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
