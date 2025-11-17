from backend.application.interfaces.idp import CurrentUserDTO
from backend.application.policies import Specification
from backend.application.vars import ShopRole


class IsOwner(Specification):
    def is_satisfied_by(self, candidate: CurrentUserDTO) -> bool:
        return candidate.role == ShopRole.OWNER


class IsManager(Specification):
    def is_satisfied_by(self, candidate: CurrentUserDTO) -> bool:
        return candidate.role == ShopRole.MANAGER


can_shop_manage_policy = IsOwner() | IsManager()
