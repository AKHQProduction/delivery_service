import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from starlette.middleware.cors import CORSMiddleware

from backend.bootstrap.config import Config
from backend.bootstrap.entrypoints.di.containers import api_container
from backend.bootstrap.logger import setup_logging
from backend.bootstrap.telemetry import instrument_fastapi, setup_telemetry
from backend.presentation.http.v1 import setup_v1_router
from backend.presentation.http.v1.routes import setup_exc_handlers

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI, /) -> AsyncIterator[None]:
    yield None


def setup_middlewares(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def create_app() -> FastAPI:
    config = Config()
    setup_logging("DEBUG" if config.app_config.debug else "INFO")

    setup_telemetry(config.otel_config)

    app = FastAPI(
        title="Water delivery API",
        docs_url="/docs",
        debug=config.app_config.debug,
        lifespan=lifespan,
        default_response_class=ORJSONResponse,
        version="2025.8",
        root_path="/api",
    )

    setup_dishka(api_container(config), app)
    setup_middlewares(app)
    setup_exc_handlers(app)
    setup_v1_router(app)

    if config.otel_config.enabled:
        instrument_fastapi(app)

    logger.info("Setup API")
    return app
