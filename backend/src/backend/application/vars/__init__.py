from datetime import date, datetime
from enum import StrEnum
from typing import NewType
from uuid import UUID
from zoneinfo import ZoneInfo

KYIV_TZ = ZoneInfo("Europe/Kyiv")


def today() -> date:
    return datetime.now(KYIV_TZ).date()


UserId = NewType("UserId", UUID)
ShopId = NewType("ShopId", UUID)
ProductId = NewType("ProductId", UUID)
CategoryId = NewType("CategoryId", UUID)
ClientId = NewType("ClientId", UUID)
OrderId = NewType("OrderId", UUID)
OrderItemId = NewType("OrderItemId", int)
AddressId = NewType("AddressId", int)
PhoneId = NewType("PhoneId", int)
TimeSlotId = NewType("TimeSlotId", UUID)
DistrictId = NewType("DistrictId", UUID)


class ShopRole(StrEnum):
    OWNER = "OWNER"
    MANAGER = "MANAGER"
    COURIER = "COURIER"


class PaymentMethod(StrEnum):
    CASH = "CASH"
    BANK_TRANSFER = "BANK_TRANSFER"
    OTHER = "OTHER"


class ExportDocType(StrEnum):
    ORDER_LIST = "ORDER_LIST"
    STATISTICS = "STATISTICS"


class RoutingMode(StrEnum):
    NONE = "NONE"
    OPTIMIZED = "OPTIMIZED"


class Empty(StrEnum):
    EMPTY = "EMPTY"
