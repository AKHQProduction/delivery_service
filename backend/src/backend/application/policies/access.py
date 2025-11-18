from backend.application.interfaces.idp import CurrentUserDTO
from backend.application.policies import Specification
from backend.application.vars import ShopId, ShopRole


class IsOwner(Specification):
    def is_satisfied_by(self, candidate: CurrentUserDTO) -> bool:
        return candidate.role == ShopRole.OWNER


class IsManager(Specification):
    def is_satisfied_by(self, candidate: CurrentUserDTO) -> bool:
        return candidate.role == ShopRole.MANAGER


can_shop_manage_policy = IsOwner() | IsManager()


class IsRelatedToShop(Specification):
    def __init__(self, shop_id: ShopId) -> None:
        self._shop_id = shop_id

    def is_satisfied_by(self, candidate: CurrentUserDTO) -> bool:
        return self._shop_id == candidate.shop_id
