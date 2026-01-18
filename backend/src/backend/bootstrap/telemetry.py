import logging
import time
from collections.abc import Iterable

from dishka import AsyncContainer
from fastapi import FastAPI
from opentelemetry import metrics, trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import (
    OTLPLogExporter,
)
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
    OTLPMetricExporter,
)
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.metrics import CallbackOptions, Meter, Observation
from opentelemetry.sdk._logs import (
    LoggerProvider,
    LoggingHandler,
)
from opentelemetry.sdk._logs.export import (
    BatchLogRecordProcessor,
)
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from sqlalchemy.ext.asyncio import AsyncEngine

from backend.bootstrap.config import OTelConfig

logger = logging.getLogger(__name__)

APP_START_TIME_UNIX = time.time()


def _get_app_start_time(options: CallbackOptions) -> Iterable[Observation]:
    yield Observation(value=APP_START_TIME_UNIX)


def setup_custom_metrics(meter: Meter) -> None:
    meter.create_observable_gauge(
        name="process_start_time_seconds",
        callbacks=[_get_app_start_time],
        description="Start time of the process since unix epoch in seconds",
    )


def setup_logging_export(resource: Resource, endpoint: str) -> None:
    logger_provider = LoggerProvider(resource=resource)
    set_logger_provider(logger_provider)

    log_exporter = OTLPLogExporter(endpoint=endpoint, insecure=True)
    logger_provider.add_log_record_processor(
        BatchLogRecordProcessor(log_exporter)
    )

    handler = LoggingHandler(
        level=logging.INFO, logger_provider=logger_provider
    )

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)


def setup_tracing(resource: Resource, endpoint: str) -> TracerProvider:
    tracer_provider = TracerProvider(resource=resource)

    span_exporter = OTLPSpanExporter(endpoint=endpoint, insecure=True)
    tracer_provider.add_span_processor(BatchSpanProcessor(span_exporter))

    trace.set_tracer_provider(tracer_provider)

    return tracer_provider


def setup_telemetry(config: OTelConfig, app: FastAPI) -> None:
    if not config.enabled:
        logger.info("OTel disabled, skipping telemetry setup")
        return

    resource = Resource.create({SERVICE_NAME: config.service_name})

    tracer_provider = setup_tracing(resource, config.exporter_endpoint)

    exporter = OTLPMetricExporter(
        endpoint=config.exporter_endpoint,
        insecure=True,
    )
    reader = PeriodicExportingMetricReader(
        exporter,
        export_interval_millis=15000,
    )

    meter_provider = MeterProvider(resource=resource, metric_readers=[reader])
    metrics.set_meter_provider(meter_provider)

    meter = metrics.get_meter(config.service_name)
    setup_custom_metrics(meter)

    setup_logging_export(resource, config.exporter_endpoint)

    RedisInstrumentor().instrument()
    LoggingInstrumentor().instrument(set_logging_format=True)
    FastAPIInstrumentor.instrument_app(
        app,
        tracer_provider=tracer_provider,
        meter_provider=meter_provider,
    )

    logger.info("Telemetry setup completed")


async def setup_db_telemetry(container: AsyncContainer) -> None:
    config = await container.get(OTelConfig)

    if not config.enabled:
        return

    engine = await container.get(AsyncEngine)
    SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)

    logger.info("SQLAlchemy instrumentation completed")
