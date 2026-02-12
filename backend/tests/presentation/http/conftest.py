from collections.abc import AsyncIterator, Callable
from io import BytesIO
from typing import Any

import pytest
import pytest_asyncio
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from openpyxl import Workbook

from backend.bootstrap.config import Config
from backend.presentation.http.v1 import setup_v1_router
from backend.presentation.http.v1.routes import setup_exc_handlers

XLSX_CONTENT_TYPE = (
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)


@pytest_asyncio.fixture
async def http_app(make_container) -> FastAPI:
    config = Config()
    app = FastAPI(root_path="/api")
    setup_v1_router(app)
    setup_exc_handlers(app)

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


@pytest.fixture()
def build_xlsx() -> Callable[[list[list[Any]]], bytes]:
    def _build(rows: list[list[Any]]) -> bytes:
        wb = Workbook()
        ws = wb.active
        ws.append(["Header row 1"])
        ws.append(["Header row 2"])
        ws.append(["Header row 3"])
        for row in rows:
            ws.append(row)
        buf = BytesIO()
        wb.save(buf)
        return buf.getvalue()

    return _build


@pytest.fixture()
def upload_xlsx(
    build_xlsx: Callable[[list[list[Any]]], bytes],
) -> Callable[[list[list[Any]], str], dict[str, Any]]:
    def _upload(
        rows: list[list[Any]],
        filename: str = "clients.xlsx",
    ) -> dict[str, Any]:
        xlsx_bytes = build_xlsx(rows)
        return {"file": (filename, xlsx_bytes, XLSX_CONTENT_TYPE)}

    return _upload
