from collections.abc import Callable
from io import BytesIO
from typing import Any

import pytest
from openpyxl import Workbook


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
