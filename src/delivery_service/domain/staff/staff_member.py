from delivery_service.domain.shared.entity import Entity
from delivery_service.domain.shared.shop_id import ShopID
from delivery_service.domain.shared.user_id import UserID
from delivery_service.domain.staff.staff_role import RoleCollection, StaffRole


class StaffMember(Entity[UserID]):
    def __init__(
        self,
        entity_id: UserID,
        *,
        roles: RoleCollection,
        shop_id: ShopID,
    ) -> None:
        super().__init__(entity_id=entity_id)

        self._roles = roles
        self._shop_id = shop_id

    def add_role(self, role: StaffRole) -> None:
        self._roles.add(role)

    @property
    def roles(self) -> RoleCollection:
        return self._roles

    @property
    def shop(self) -> ShopID:
        return self._shop_id
