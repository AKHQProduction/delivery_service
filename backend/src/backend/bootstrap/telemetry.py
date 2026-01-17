import logging

from dishka import AsyncContainer
from fastapi import FastAPI
from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
    OTLPMetricExporter,
)
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from sqlalchemy.ext.asyncio import AsyncEngine

from backend.bootstrap.config import OTelConfig

logger = logging.getLogger(__name__)


async def setup_telemetry(app: FastAPI, container: AsyncContainer) -> None:
    config = await container.get(OTelConfig)

    if not config.enabled:
        logger.info("OTel disabled, skipping telemetry setup")
        return

    resource = Resource.create({SERVICE_NAME: config.service_name})

    exporter = OTLPMetricExporter(
        endpoint=config.exporter_endpoint,
        insecure=True,
    )
    reader = PeriodicExportingMetricReader(
        exporter,
        export_interval_millis=15000,
    )

    provider = MeterProvider(resource=resource, metric_readers=[reader])
    metrics.set_meter_provider(provider)

    RedisInstrumentor().instrument()
    LoggingInstrumentor().instrument()
    FastAPIInstrumentor.instrument_app(app)

    engine = await container.get(AsyncEngine)
    SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)

    logger.info("Telemetry setup completed")
