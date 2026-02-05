from dataclasses import dataclass

from backend.application.vars import DistrictId, ShopId


@dataclass(frozen=True)
class DistrictReadModel:
    district_id: DistrictId
    name: str


@dataclass(frozen=True)
class GetDistrictsFilters:
    shop_id: ShopId | None = None
    name: str | None = None
