"""OpenTelemetry instrumentation setup."""

import logging
from typing import Optional

from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

from mitlist.core.config import settings

logger = logging.getLogger(__name__)


def setup_otel() -> Optional[FastAPIInstrumentor]:
    """
    Initialize OpenTelemetry instrumentation.

    Returns FastAPIInstrumentor instance if configured, None otherwise.
    Keeps exporter configurable - can be extended to use OTLP exporter.
    """
    if not settings.OTEL_EXPORTER_OTLP_ENDPOINT and settings.is_development:
        # Development: use console exporter
        provider = TracerProvider()
        processor = BatchSpanProcessor(ConsoleSpanExporter())
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)
        logger.info("OpenTelemetry configured with console exporter")
    elif settings.OTEL_EXPORTER_OTLP_ENDPOINT:
        # Production: OTLP exporter would be configured here
        # For now, just set up the provider
        provider = TracerProvider()
        trace.set_tracer_provider(provider)
        logger.info(
            f"OpenTelemetry configured with OTLP endpoint: {settings.OTEL_EXPORTER_OTLP_ENDPOINT}"
        )
    else:
        logger.info("OpenTelemetry not configured")
        return None

    # Instrument logging
    LoggingInstrumentor().instrument()

    # Return FastAPI instrumentor (will be applied in main.py)
    return FastAPIInstrumentor()
