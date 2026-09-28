import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("api_access")

class RequestCorrelationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Generate or retain request correlation ID
        correlation_id = request.headers.get("X-Request-ID") or f"req_{uuid.uuid4().hex[:12]}"
        request.state.correlation_id = correlation_id

        start_time = time.time()
        response: Response = await call_next(request)
        duration_ms = round((time.time() - start_time) * 1000, 2)

        response.headers["X-Request-ID"] = correlation_id
        response.headers["X-Response-Time"] = f"{duration_ms}ms"

        # Non-sensitive access log
        if not request.url.path.startswith(("/static", "/favicon")):
            logger.info(
                f"[{correlation_id}] {request.method} {request.url.path} -> {response.status_code} ({duration_ms}ms)"
            )

        return response
