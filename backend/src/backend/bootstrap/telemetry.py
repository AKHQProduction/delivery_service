import logging
import time
from collections.abc import Iterable

from dishka import AsyncContainer
from fastapi import FastAPI
from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
    OTLPMetricExporter,
)
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.metrics import CallbackOptions, Meter, Observation
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
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


def setup_telemetry(config: OTelConfig, app: FastAPI) -> None:
    if not config.enabled:
        logger.info("OTel disabled, skipping telemetry setup")
        return

    resource = Resource.create({SERVICE_NAME: config.service_name})

    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)

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

    RedisInstrumentor().instrument()
    LoggingInstrumentor().instrument()
    FastAPIInstrumentor.instrument_app(app, meter_provider=meter_provider)

    logger.info("Telemetry setup completed")


async def setup_db_telemetry(container: AsyncContainer) -> None:
    config = await container.get(OTelConfig)

    if not config.enabled:
        return

    engine = await container.get(AsyncEngine)
    SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)

    logger.info("SQLAlchemy instrumentation completed")
