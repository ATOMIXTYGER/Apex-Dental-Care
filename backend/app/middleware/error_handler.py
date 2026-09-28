import logging

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("dental_app")

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Normalize HTTPException to standard API error schema."""
    code = "HTTP_ERROR"
    message = str(exc.detail)
    details = None

    if isinstance(exc.detail, dict):
        code = exc.detail.get("code", code)
        message = exc.detail.get("message", message)
        details = exc.detail.get("details", None)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details
            }
        },
        headers=getattr(exc, "headers", None)
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Normalize RequestValidationError without leaking internal models."""
    errors = []
    for err in exc.errors():
        field_loc = " -> ".join([str(x) for x in err.get("loc", []) if x != "body"])
        errors.append({
            "field": field_loc,
            "message": err.get("msg", "Invalid value"),
            "type": err.get("type", "value_error")
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Input validation failed. Please check the submitted fields.",
                "details": {"validation_errors": errors}
            }
        }
    )

async def unhandled_exception_handler(request: Request, exc: Exception):
    """Catch-all for unhandled exceptions to prevent leaking server traces."""
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc!s}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred while processing your request. Please contact system support.",
                "details": None
            }
        }
    )
