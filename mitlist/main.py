"""FastAPI application factory and main entry point."""

import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from mitlist.api.router import api_router, health_router
from mitlist.core.config import settings
from mitlist.core.errors import AppError, app_error_handler
from mitlist.core.logging import setup_logging
from mitlist.core.otel import setup_otel
from mitlist.core.request_context import set_trace_id

logger = logging.getLogger(__name__)


def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle FastAPI validation errors with RFC 7807 format."""
    from mitlist.core.request_context import get_trace_id

    trace_id = get_trace_id()
    errors = exc.errors()
    return JSONResponse(
        status_code=422,
        content={
            "type": "error:validation",
            "code": "VALIDATION_ERROR",
            "detail": "Request validation failed",
            "instance": str(request.url.path),
            "trace_id": trace_id,
            "errors": errors,
        },
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown logic."""
    # Startup
    logger.info(f"Starting {settings.PROJECT_NAME} in {settings.ENVIRONMENT} environment")
    setup_logging()
    otel_instrumentor = setup_otel()
    if otel_instrumentor:
        otel_instrumentor.instrument_app(app)

    yield

    # Shutdown
    logger.info(f"Shutting down {settings.PROJECT_NAME}")


def create_application() -> FastAPI:
    """
    Application factory function.

    Creates and configures the FastAPI application instance.
    """
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version="0.1.0",
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
        lifespan=lifespan,
    )

    # CORS middleware
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.is_development else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Trace ID middleware
    @application.middleware("http")
    async def trace_id_middleware(request: Request, call_next):
        """Ensure every request has a trace_id."""
        trace_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        set_trace_id(trace_id)
        response = await call_next(request)
        response.headers["X-Request-ID"] = trace_id
        return response

    # Exception handlers
    application.add_exception_handler(AppError, app_error_handler)
    application.add_exception_handler(RequestValidationError, validation_error_handler)

    # Include routers
    application.include_router(health_router)
    application.include_router(api_router)

    return application


# Create app instance
app = create_application()
