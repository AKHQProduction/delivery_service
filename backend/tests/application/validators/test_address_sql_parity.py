import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.validators.address import (
    HOUSE_LETTER_SQL_RE,
    HOUSE_LETTER_SQL_REPL,
    STREET_PREFIX_SQL_RE,
    normalize_house,
    normalize_street,
)

STREET_CASES = [
    "вулиця Василя Сліпака",
    "вул. Василя Сліпака",
    "вул Василя Сліпака",
    "улица Шевченко",
    "ул. Шевченко",
    "проспект Шевченка",
    "просп. Шевченка",
    "пр. Шевченка",
    "бульвар Лесі Українки",
    "б-р Лесі Українки",
    "провулок Тихий",
    "переулок Тихий",
    "мікрорайон Сонячний",
    "мкр. Сонячний",
    "шосе Харківське",
    "ш. Харківське",
    "набережна Перемоги",
    "наб. Перемоги",
    "площа Ринок",
    "пл. Ринок",
    "тупік Глухий",
    "туп. Глухий",
    "узвіз Андріївський",
    "узв. Андріївський",
    "алея Паркова",
    "ал. Паркова",
    "Василя Сліпака",
    "вулична",
    "  Хрещатик  ",
    "пр-т Перемоги",
    "пр-кт Перемоги",
    "м-н Сонячний",
]

HOUSE_CASES = [
    "15",
    "15 а",
    "15-а",
    "15А",
    "15–б",
    "15—б",
    "15a",
    "  15  ",
    "15/2",
    "15 - А",
    "7 б",
    "123в",
]


@pytest.mark.asyncio()
@pytest.mark.parametrize("street", STREET_CASES)
async def test_normalize_street_sql_parity(
    session: AsyncSession, street: str
) -> None:
    python_result = normalize_street(street)

    sql = text(
        "SELECT btrim(regexp_replace(  lower(btrim(:street)),  :pattern,  ''))"
    )
    row = await session.execute(
        sql, {"street": street, "pattern": STREET_PREFIX_SQL_RE}
    )
    sql_result = row.scalar()

    assert sql_result == python_result, (
        f"Mismatch for {street!r}: "
        f"python={python_result!r}, sql={sql_result!r}"
    )


@pytest.mark.asyncio()
@pytest.mark.parametrize("house", HOUSE_CASES)
async def test_normalize_house_sql_parity(
    session: AsyncSession, house: str
) -> None:
    python_result = normalize_house(house)

    sql = text(
        "SELECT regexp_replace("
        "  lower(btrim(:house)),"
        "  :pattern,"
        "  :repl,"
        "  'g'"
        ")"
    )
    row = await session.execute(
        sql,
        {
            "house": house,
            "pattern": HOUSE_LETTER_SQL_RE,
            "repl": HOUSE_LETTER_SQL_REPL,
        },
    )
    sql_result = row.scalar()

    assert sql_result == python_result, (
        f"Mismatch for {house!r}: python={python_result!r}, sql={sql_result!r}"
    )
