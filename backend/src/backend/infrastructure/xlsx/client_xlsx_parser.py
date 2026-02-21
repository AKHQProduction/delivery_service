import logging
from dataclasses import dataclass
from enum import StrEnum
from io import BytesIO

from openpyxl import load_workbook
from openpyxl.cell.read_only import EmptyCell

logger = logging.getLogger(__name__)

DATA_START_ROW = 4
MAX_COL = 19

COL_FULL_NAME = 1
COL_PHONE1 = 2
COL_PHONE2 = 3
COL_ADDR1_STREET = 4
COL_ADDR1_HOUSE = 5
COL_ADDR1_APARTMENT = 6
COL_ADDR1_ENTRANCE = 7
COL_ADDR1_FLOOR = 8
COL_ADDR1_INTERCOM = 9
COL_ADDR1_DISTRICT = 10
COL_ADDR1_COMMENT = 11
COL_ADDR2_STREET = 12
COL_ADDR2_HOUSE = 13
COL_ADDR2_APARTMENT = 14
COL_ADDR2_ENTRANCE = 15
COL_ADDR2_FLOOR = 16
COL_ADDR2_INTERCOM = 17
COL_ADDR2_DISTRICT = 18
COL_ADDR2_COMMENT = 19

RawCellValues = tuple[str | None, ...]


class ImportErrorKind(StrEnum):
    EMPTY_FIELD = "Пусте поле"
    DUPLICATE_IN_DB = "Дубль (у базі)"
    DUPLICATE_IN_FILE = "Дубль у файлі"
    INVALID_PHONE = "Невалідний телефон"


@dataclass(frozen=True)
class ParsedAddress:
    street: str
    house: str
    apartment: str | None
    entrance: str | None
    floor: str | None
    intercom: str | None
    district_name: str | None
    comment: str | None


@dataclass(frozen=True)
class ParsedClientRow:
    row_number: int
    full_name: str
    phone1: str
    phone2: str | None
    address1: ParsedAddress
    address2: ParsedAddress | None


@dataclass(frozen=True)
class RejectedClientRow:
    row_number: int
    raw_values: RawCellValues
    error_kind: ImportErrorKind
    error_detail: str | None = None

    @property
    def error_message(self) -> str:
        if self.error_detail:
            return f"{self.error_kind.value} ({self.error_detail})"
        return self.error_kind.value


@dataclass(frozen=True)
class ParseResult:
    valid: list[ParsedClientRow]
    rejected: list[RejectedClientRow]
    raw_by_row: dict[int, RawCellValues]


class ClientXlsxParser:
    def parse(self, file_bytes: bytes) -> ParseResult:
        wb = load_workbook(BytesIO(file_bytes), read_only=True, data_only=True)
        ws = wb.active
        if ws is None:
            wb.close()
            return ParseResult(valid=[], rejected=[], raw_by_row={})

        valid: list[ParsedClientRow] = []
        rejected: list[RejectedClientRow] = []
        raw_by_row: dict[int, RawCellValues] = {}

        for row_idx, row in enumerate(
            ws.iter_rows(min_row=DATA_START_ROW, values_only=False),
            start=DATA_START_ROW,
        ):
            cells: dict[int, object] = {}
            for cell in row:
                if not isinstance(cell, EmptyCell) and cell.column is not None:
                    cells[cell.column] = cell.value

            raw = tuple(_str(cells.get(col)) for col in range(1, MAX_COL + 1))
            raw_by_row[row_idx] = raw

            full_name = _str(cells.get(COL_FULL_NAME))
            phone1 = _str(cells.get(COL_PHONE1))
            street1 = _str(cells.get(COL_ADDR1_STREET))
            house1 = _str(cells.get(COL_ADDR1_HOUSE))

            if not full_name or not phone1 or not street1 or not house1:
                if any(v is not None for v in raw):
                    rejected.append(
                        RejectedClientRow(
                            row_number=row_idx,
                            raw_values=raw,
                            error_kind=ImportErrorKind.EMPTY_FIELD,
                        )
                    )
                continue

            address1 = ParsedAddress(
                street=street1,
                house=house1,
                apartment=_str(cells.get(COL_ADDR1_APARTMENT)),
                entrance=_str(cells.get(COL_ADDR1_ENTRANCE)),
                floor=_str(cells.get(COL_ADDR1_FLOOR)),
                intercom=_str(cells.get(COL_ADDR1_INTERCOM)),
                district_name=_str(cells.get(COL_ADDR1_DISTRICT)),
                comment=_str(cells.get(COL_ADDR1_COMMENT)),
            )

            street2 = _str(cells.get(COL_ADDR2_STREET))
            house2 = _str(cells.get(COL_ADDR2_HOUSE))
            address2: ParsedAddress | None = None
            if street2 and house2:
                address2 = ParsedAddress(
                    street=street2,
                    house=house2,
                    apartment=_str(cells.get(COL_ADDR2_APARTMENT)),
                    entrance=_str(cells.get(COL_ADDR2_ENTRANCE)),
                    floor=_str(cells.get(COL_ADDR2_FLOOR)),
                    intercom=_str(cells.get(COL_ADDR2_INTERCOM)),
                    district_name=_str(cells.get(COL_ADDR2_DISTRICT)),
                    comment=_str(cells.get(COL_ADDR2_COMMENT)),
                )

            valid.append(
                ParsedClientRow(
                    row_number=row_idx,
                    full_name=full_name,
                    phone1=phone1,
                    phone2=_str(cells.get(COL_PHONE2)),
                    address1=address1,
                    address2=address2,
                )
            )

        wb.close()
        logger.info(
            "Parsed XLSX: %d valid, %d rejected rows",
            len(valid),
            len(rejected),
        )
        return ParseResult(
            valid=valid, rejected=rejected, raw_by_row=raw_by_row
        )


def _str(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
