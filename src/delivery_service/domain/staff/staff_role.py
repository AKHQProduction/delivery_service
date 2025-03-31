from enum import Enum
from typing import NewType

from delivery_service.domain.shared.entity import Entity

StaffRoleID = NewType("StaffRoleID", int)


class Role(Enum):
    SHOP_OWNER = "shop_owner"
    SHOP_MANAGER = "shop_manager"
    COURIER = "courier"
    USER = "user"


class StaffRole(Entity[StaffRoleID]):
    def __init__(self, entity_id: StaffRoleID, *, role_name: Role) -> None:
        super().__init__(entity_id=entity_id)

        self._name = role_name

    @property
    def name(self) -> Role:
        return self._name

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(Id: {self._entity_id}, name: {self._name})"
        )

    def __str__(self) -> str:
        return self.__repr__()


class RoleCollection(list[StaffRole]):
    def __init__(self, roles: list[StaffRole] | None = None):
        if roles:
            list.__init__(self, roles)
        else:
            list.__init__(self)

    def add(self, element: StaffRole) -> None:
        if element in self:
            raise ValueError()
        super().append(element)

    def get(self, role_id: StaffRoleID) -> StaffRole:
        for role in self:
            if role.entity_id == role_id:
                return role
        raise ValueError()

    def discard(self, element: StaffRole) -> None:
        if element in self:
            return super().remove(element)
        raise ValueError()

    def __repr__(self) -> str:
        roles = ", ".join(repr(role) for role in self)
        return f"{self.__class__.__name__}([{roles}])"

    def __str__(self) -> str:
        return self.__repr__()
