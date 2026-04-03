from collections.abc import Callable
from io import BytesIO
from typing import Any

from openpyxl import Workbook

from backend.infrastructure.xlsx.client_xlsx_parser import (
    MAX_COL,
    ClientXlsxParser,
    ImportErrorKind,
)
from backend.infrastructure.xlsx.column_mapping import SystemField


def _valid_row(
    full_name: str = "Іван Іванов",
    phone1: str = "+380501234567",
    phone2: str | None = None,
    street1: str = "Хрещатик",
    house1: str = "10",
    *,
    extra: list[Any] | None = None,
) -> list[Any]:
    row: list[Any] = [full_name, phone1, phone2, street1, house1]
    if extra:
        row.extend(extra)
    return row


class TestClientXlsxParser:
    def test_parse_valid_rows(
        self, build_xlsx: Callable[[list[list[Any]]], bytes]
    ):
        xlsx = build_xlsx([
            _valid_row(),
            _valid_row(
                full_name="Петро Петренко",
                phone1="+380931234567",
                street1="Садова",
                house1="22",
            ),
        ])
        result = ClientXlsxParser().parse(xlsx)
        assert len(result.valid) == 2
        assert len(result.rejected) == 0

    def test_parse_missing_full_name(
        self, build_xlsx: Callable[[list[list[Any]]], bytes]
    ):
        xlsx = build_xlsx([
            [None, "+380501234567", None, "Хрещатик", "10"],
        ])
        result = ClientXlsxParser().parse(xlsx)
        assert len(result.valid) == 0
        assert len(result.rejected) == 1
        assert result.rejected[0].error_kind == ImportErrorKind.EMPTY_FIELD

    def test_parse_missing_phone(
        self, build_xlsx: Callable[[list[list[Any]]], bytes]
    ):
        xlsx = build_xlsx([
            ["Іван", None, None, "Хрещатик", "10"],
        ])
        result = ClientXlsxParser().parse(xlsx)
        assert len(result.valid) == 0
        assert len(result.rejected) == 1
        assert result.rejected[0].error_kind == ImportErrorKind.EMPTY_FIELD

    def test_parse_missing_street(
        self, build_xlsx: Callable[[list[list[Any]]], bytes]
    ):
        xlsx = build_xlsx([
            ["Іван", "+380501234567", None, None, "10"],
        ])
        result = ClientXlsxParser().parse(xlsx)
        assert len(result.valid) == 0
        assert len(result.rejected) == 1
        assert result.rejected[0].error_kind == ImportErrorKind.EMPTY_FIELD

    def test_parse_missing_house(
        self, build_xlsx: Callable[[list[list[Any]]], bytes]
    ):
        xlsx = build_xlsx([
            ["Іван", "+380501234567", None, "Хрещатик", None],
        ])
        result = ClientXlsxParser().parse(xlsx)
        assert len(result.valid) == 0
        assert len(result.rejected) == 1
        assert result.rejected[0].error_kind == ImportErrorKind.EMPTY_FIELD

    def test_parse_empty_row_skipped(
        self, build_xlsx: Callable[[list[list[Any]]], bytes]
    ):
        xlsx = build_xlsx([
            [None, None, None, None, None],
        ])
        result = ClientXlsxParser().parse(xlsx)
        assert len(result.valid) == 0
        assert len(result.rejected) == 0

    def test_parse_mix_valid_and_invalid(
        self, build_xlsx: Callable[[list[list[Any]]], bytes]
    ):
        xlsx = build_xlsx([
            _valid_row(),
            [None, "+380501234567", None, "Хрещатик", "10"],
        ])
        result = ClientXlsxParser().parse(xlsx)
        assert len(result.valid) == 1
        assert len(result.rejected) == 1

    def test_raw_by_row_populated(
        self, build_xlsx: Callable[[list[list[Any]]], bytes]
    ):
        xlsx = build_xlsx([
            _valid_row(),
            ["Без телефону", None, None, "Хрещатик", "10"],
        ])
        result = ClientXlsxParser().parse(xlsx)
        assert 4 in result.raw_by_row
        assert 5 in result.raw_by_row

    def test_raw_values_length(
        self, build_xlsx: Callable[[list[list[Any]]], bytes]
    ):
        xlsx = build_xlsx([_valid_row()])
        result = ClientXlsxParser().parse(xlsx)
        for raw in result.raw_by_row.values():
            assert len(raw) == MAX_COL

    def test_parse_empty_file(
        self, build_xlsx: Callable[[list[list[Any]]], bytes]
    ):
        xlsx = build_xlsx([])
        result = ClientXlsxParser().parse(xlsx)
        assert result.valid == []
        assert result.rejected == []

    def test_parse_optional_address2(
        self, build_xlsx: Callable[[list[list[Any]]], bytes]
    ):
        xlsx = build_xlsx([
            [
                "Клієнт",
                "+380501234567",
                None,
                "Хрещатик",
                "10",
                None,
                None,
                None,
                None,
                None,
                None,
                "Садова",
                "22",
            ],
        ])
        result = ClientXlsxParser().parse(xlsx)
        assert len(result.valid) == 1
        assert result.valid[0].address2 is not None
        assert result.valid[0].address2.street == "Садова"
        assert result.valid[0].address2.house == "22"

    def test_parse_address2_requires_both_street_and_house(
        self, build_xlsx: Callable[[list[list[Any]]], bytes]
    ):
        xlsx = build_xlsx([
            [
                "Клієнт",
                "+380501234567",
                None,
                "Хрещатик",
                "10",
                None,
                None,
                None,
                None,
                None,
                None,
                "Садова",
                None,
            ],
        ])
        result = ClientXlsxParser().parse(xlsx)
        assert len(result.valid) == 1
        assert result.valid[0].address2 is None


def _build_mapped_xlsx(
    rows: list[list[Any]],
    *,
    header_row: list[Any] | None = None,
) -> bytes:
    wb = Workbook()
    ws = wb.active
    if header_row:
        ws.append(header_row)
    for row in rows:
        ws.append(row)
    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()


class TestClientXlsxParserWithMapping:
    def test_parse_with_custom_mapping(self):
        mapping = {
            3: SystemField.FULL_NAME,
            1: SystemField.PHONE1,
            5: SystemField.ADDR1_STREET,
            2: SystemField.ADDR1_HOUSE,
        }
        xlsx = _build_mapped_xlsx(
            header_row=["Телефон", "Будинок", "Ім'я", "Зайве", "Вулиця"],
            rows=[
                ["+380501234567", "10", "Іван Іванов", "щось", "Хрещатик"],
            ],
        )
        result = ClientXlsxParser().parse(
            xlsx, column_mapping=mapping, data_start_row=2
        )
        assert len(result.valid) == 1
        assert result.valid[0].full_name == "Іван Іванов"
        assert result.valid[0].phone1 == "+380501234567"
        assert result.valid[0].address1.street == "Хрещатик"
        assert result.valid[0].address1.house == "10"

    def test_parse_with_mapping_no_headers(self):
        mapping = {
            1: SystemField.FULL_NAME,
            2: SystemField.PHONE1,
            3: SystemField.ADDR1_STREET,
            4: SystemField.ADDR1_HOUSE,
        }
        xlsx = _build_mapped_xlsx(
            rows=[
                ["Іван", "+380501234567", "Хрещатик", "10"],
            ],
        )
        result = ClientXlsxParser().parse(
            xlsx, column_mapping=mapping, data_start_row=1
        )
        assert len(result.valid) == 1
        assert result.valid[0].full_name == "Іван"

    def test_parse_with_mapping_missing_required_field(self):
        mapping = {
            1: SystemField.FULL_NAME,
            2: SystemField.PHONE1,
            3: SystemField.ADDR1_STREET,
            4: SystemField.ADDR1_HOUSE,
        }
        xlsx = _build_mapped_xlsx(
            rows=[
                [None, "+380501234567", "Хрещатик", "10"],
            ],
        )
        result = ClientXlsxParser().parse(
            xlsx, column_mapping=mapping, data_start_row=1
        )
        assert len(result.valid) == 0
        assert len(result.rejected) == 1
        assert result.rejected[0].error_kind == ImportErrorKind.EMPTY_FIELD

    def test_parse_with_mapping_optional_fields(self):
        mapping = {
            1: SystemField.FULL_NAME,
            2: SystemField.PHONE1,
            3: SystemField.ADDR1_STREET,
            4: SystemField.ADDR1_HOUSE,
            5: SystemField.ADDR1_APARTMENT,
            6: SystemField.ADDR1_DISTRICT,
        }
        xlsx = _build_mapped_xlsx(
            rows=[
                ["Іван", "+380501234567", "Хрещатик", "10", "5", "Центр"],
            ],
        )
        result = ClientXlsxParser().parse(
            xlsx, column_mapping=mapping, data_start_row=1
        )
        assert len(result.valid) == 1
        assert result.valid[0].address1.apartment == "5"
        assert result.valid[0].address1.district_name == "Центр"

    def test_legacy_still_works(
        self, build_xlsx: Callable[[list[list[Any]]], bytes]
    ):
        xlsx = build_xlsx([_valid_row()])
        result = ClientXlsxParser().parse(xlsx)
        assert len(result.valid) == 1
        assert result.valid[0].full_name == "Іван Іванов"

    def test_raw_by_row_uses_mapped_max_col(self):
        mapping = {
            1: SystemField.FULL_NAME,
            2: SystemField.PHONE1,
            5: SystemField.ADDR1_STREET,
            7: SystemField.ADDR1_HOUSE,
        }
        xlsx = _build_mapped_xlsx(
            rows=[
                ["Іван", "+380501234567", "x", "y", "Хрещатик", "z", "10"],
            ],
        )
        result = ClientXlsxParser().parse(
            xlsx, column_mapping=mapping, data_start_row=1
        )
        for raw in result.raw_by_row.values():
            assert len(raw) == 7
