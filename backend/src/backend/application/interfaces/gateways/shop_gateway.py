from dataclasses import dataclass

from backend.application.vars import ShopId, ShopRole, UserId


@dataclass(frozen=True)
class EmployeeReadModel:
    user_id: UserId
    full_name: str
    role: ShopRole


@dataclass(frozen=True)
class EmployeeFilters:
    shop_id: ShopId | None = None
    name: str | None = None
