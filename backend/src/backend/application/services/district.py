from backend.application.vars import DistrictId, ShopId
from backend.infrastructure.persistence.tables.districts import District


def create_district(
    *,
    district_id: DistrictId,
    shop_id: ShopId,
    name: str,
) -> District:
    return District(id=district_id, shop_id=shop_id, name=name)


def update_district(district: District, *, name: str) -> None:
    district.name = name
