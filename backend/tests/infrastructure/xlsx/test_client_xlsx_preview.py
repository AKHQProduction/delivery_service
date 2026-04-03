from io import BytesIO
from typing import Any

from openpyxl import Workbook

from backend.infrastructure.xlsx.client_xlsx_preview import preview_xlsx


def _build_simple_xlsx(rows: list[list[Any]]) -> bytes:
    wb = Workbook()
    ws = wb.active
    for row in rows:
        ws.append(row)
    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()


class TestPreviewXlsx:
    def test_preview_with_headers_and_data(self):
        xlsx = _build_simple_xlsx([
            ["ПІБ", "Телефон", "Вулиця"],
            ["Іван Іванов", "+380501234567", "Хрещатик"],
            ["Петро Петренко", "+380931234567", "Садова"],
        ])
        result = preview_xlsx(xlsx)
        assert len(result.columns) == 3
        assert result.columns[0].index == 1
        assert result.columns[0].header == "ПІБ"
        assert result.columns[0].sample_values == [
            "Іван Іванов",
            "Петро Петренко",
        ]
        assert result.total_rows == 2

    def test_preview_empty_file(self):
        xlsx = _build_simple_xlsx([])
        result = preview_xlsx(xlsx)
        assert result.columns == []
        assert result.total_rows == 0

    def test_preview_only_headers(self):
        xlsx = _build_simple_xlsx([
            ["ПІБ", "Телефон"],
        ])
        result = preview_xlsx(xlsx)
        assert len(result.columns) == 2
        assert result.columns[0].header == "ПІБ"
        assert result.columns[0].sample_values == []
        assert result.total_rows == 0

    def test_preview_no_headers_only_data(self):
        xlsx = _build_simple_xlsx([
            ["Іван", "+380501234567"],
            ["Петро", "+380931234567"],
        ])
        result = preview_xlsx(xlsx)
        assert len(result.columns) == 2
        assert result.columns[0].header == "Іван"
        assert result.columns[0].sample_values == ["Петро"]
        assert result.total_rows == 1

    def test_preview_filters_empty_columns(self):
        xlsx = _build_simple_xlsx([
            ["ПІБ", None, "Вулиця"],
            ["Іван", None, "Хрещатик"],
        ])
        result = preview_xlsx(xlsx)
        assert len(result.columns) == 2
        indexes = [c.index for c in result.columns]
        assert 1 in indexes
        assert 3 in indexes
        assert 2 not in indexes

    def test_preview_sample_values_filter_none(self):
        xlsx = _build_simple_xlsx([
            ["ПІБ", "Телефон"],
            ["Іван", None],
            [None, "+380501234567"],
        ])
        result = preview_xlsx(xlsx)
        pib_col = result.columns[0]
        assert pib_col.sample_values == ["Іван"]
        phone_col = result.columns[1]
        assert phone_col.sample_values == ["+380501234567"]
