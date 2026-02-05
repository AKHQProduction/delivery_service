from backend.application.dto.idp import CurrentUserDTO
from backend.application.errors import AccessDeniedError
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


def ensure_can_manage(current_user: CurrentUserDTO) -> None:
    if not can_shop_manage_policy.is_satisfied_by(current_user):
        raise AccessDeniedError


def ensure_is_owner(current_user: CurrentUserDTO) -> None:
    if not IsOwner().is_satisfied_by(current_user):
        raise AccessDeniedError


def ensure_related_to_shop(
    current_user: CurrentUserDTO,
    shop_id: ShopId,
) -> None:
    if not IsRelatedToShop(shop_id).is_satisfied_by(current_user):
        raise AccessDeniedError
