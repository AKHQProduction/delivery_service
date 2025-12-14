import logging
from typing import TYPE_CHECKING

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
    OTLPMetricExporter,
)
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import (
    DEPLOYMENT_ENVIRONMENT,
    SERVICE_NAME,
    Resource,
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

if TYPE_CHECKING:
    from fastapi import FastAPI
    from sqlalchemy.ext.asyncio import AsyncEngine

    from backend.bootstrap.config import OTELConfig

logger = logging.getLogger(__name__)


def _create_resource(config: "OTELConfig") -> Resource:
    return Resource.create({
        SERVICE_NAME: config.service_name,
        DEPLOYMENT_ENVIRONMENT: config.environment,
    })


def _setup_tracing(config: "OTELConfig", resource: Resource) -> None:
    exporter = OTLPSpanExporter(endpoint=config.otlp_endpoint, insecure=True)
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    logger.info("Tracing configured: endpoint=%s", config.otlp_endpoint)


def _setup_metrics(config: "OTELConfig", resource: Resource) -> None:
    exporter = OTLPMetricExporter(endpoint=config.otlp_endpoint, insecure=True)
    reader = PeriodicExportingMetricReader(
        exporter, export_interval_millis=15000
    )
    provider = MeterProvider(resource=resource, metric_readers=[reader])
    metrics.set_meter_provider(provider)
    logger.info("Metrics configured: endpoint=%s", config.otlp_endpoint)


def _setup_logging_instrumentation() -> None:
    LoggingInstrumentor().instrument(set_logging_format=True)
    logger.info("Logging instrumentation configured")


def setup_telemetry(config: "OTELConfig") -> None:
    if not config.enabled:
        logger.info("OpenTelemetry disabled (OTEL_ENABLED=false)")
        return

    resource = _create_resource(config)
    _setup_tracing(config, resource)
    _setup_metrics(config, resource)
    _setup_logging_instrumentation()

    logger.info(
        "OpenTelemetry initialized: service=%s, env=%s",
        config.service_name,
        config.environment,
    )


def instrument_fastapi(app: "FastAPI") -> None:
    FastAPIInstrumentor.instrument_app(app)
    logger.info("FastAPI instrumented")


def instrument_sqlalchemy(engine: "AsyncEngine") -> None:
    SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)
    logger.info("SQLAlchemy instrumented")
