from collections.abc import AsyncIterator, Callable
from typing import Any

import pytest
import pytest_asyncio
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from backend.bootstrap.config import Config
from backend.presentation.http.v1 import setup_v1_router


@pytest_asyncio.fixture
async def http_app(make_container) -> FastAPI:
    config = Config()
    app = FastAPI(root_path="/api")
    setup_v1_router(app)

    container = make_container(config)
    setup_dishka(container, app)
    return app


@pytest_asyncio.fixture
async def http_client(http_app: FastAPI) -> AsyncIterator[AsyncClient]:
    async with AsyncClient(
        transport=ASGITransport(app=http_app), base_url="http://"
    ) as client:
        yield client


@pytest.fixture()
def customer_headers() -> Callable[[int], dict[str, Any]]:
    def _factory(user_id: int) -> dict[str, Any]:
        return {"Authorization": f"Bearer {user_id}"}

    return _factory
