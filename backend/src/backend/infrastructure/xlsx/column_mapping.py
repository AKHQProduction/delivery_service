from collections import Counter
from enum import StrEnum

ColumnMapping = dict[int, "SystemField"]


class SystemField(StrEnum):
    FULL_NAME = "full_name"
    PHONE1 = "phone1"
    PHONE2 = "phone2"
    ADDR1_STREET = "addr1_street"
    ADDR1_HOUSE = "addr1_house"
    ADDR1_APARTMENT = "addr1_apartment"
    ADDR1_ENTRANCE = "addr1_entrance"
    ADDR1_FLOOR = "addr1_floor"
    ADDR1_INTERCOM = "addr1_intercom"
    ADDR1_DISTRICT = "addr1_district"
    ADDR1_COMMENT = "addr1_comment"
    ADDR2_STREET = "addr2_street"
    ADDR2_HOUSE = "addr2_house"
    ADDR2_APARTMENT = "addr2_apartment"
    ADDR2_ENTRANCE = "addr2_entrance"
    ADDR2_FLOOR = "addr2_floor"
    ADDR2_INTERCOM = "addr2_intercom"
    ADDR2_DISTRICT = "addr2_district"
    ADDR2_COMMENT = "addr2_comment"


REQUIRED_FIELDS: frozenset[SystemField] = frozenset({
    SystemField.FULL_NAME,
    SystemField.PHONE1,
    SystemField.ADDR1_STREET,
    SystemField.ADDR1_HOUSE,
})


def validate_mapping(mapping: ColumnMapping) -> list[str]:
    mapped_fields = set(mapping.values())

    missing = REQUIRED_FIELDS - mapped_fields
    errors = [
        f"Required field not mapped: {field.value}"
        for field in sorted(missing, key=lambda f: f.value)
    ]

    errors.extend(
        f"Field {field.value} mapped to multiple columns"
        for field, count in Counter(mapping.values()).items()
        if count > 1
    )

    return errors
