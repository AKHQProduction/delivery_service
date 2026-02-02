from dataclasses import dataclass

from backend.application.vars import ShopId, ShopRole, UserId


@dataclass(frozen=True)
class CurrentUserDTO:
    user_id: UserId
    full_name: str
    role: ShopRole
    shop_id: ShopId
