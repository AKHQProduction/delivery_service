from enum import Enum, auto
from typing import ClassVar

from application.employee.gateway import EmployeeReader
from application.errors.access import AccessDeniedError
from entities.employee.models import Employee
from entities.shop.models import ShopId
from entities.user.models import UserId


class Permission(Enum):
    CAN_CREATE_SHOP = auto()
    CAN_EDIT_SHOP = auto()
    CAN_DELETE_SHOP = auto()
    CAN_CREATE_EMPLOYEE = auto()
    CAN_EDIT_EMPLOYEE = auto()
    CAN_CREATE_GOODS = auto()


class RolePermission(Enum):
    ADMIN: ClassVar[set[Permission]] = {
        Permission.CAN_EDIT_SHOP,
        Permission.CAN_DELETE_SHOP,
        Permission.CAN_CREATE_EMPLOYEE,
        Permission.CAN_EDIT_EMPLOYEE,
        Permission.CAN_CREATE_GOODS,
    }
    DEFAULT: ClassVar[set[Permission]] = {
        Permission.CAN_CREATE_SHOP,
    }


class AccessService:
    def __init__(
        self,
        employee_reader: EmployeeReader,
    ) -> None:
        self._employee_reader = employee_reader

    @staticmethod
    def _has_permission(
        employee: Employee | None,
        permission: Permission,
        shop_id: ShopId | None = None,
    ) -> bool:
        if not employee:
            return permission in RolePermission.DEFAULT.value

        try:
            return (
                employee.shop_id == shop_id
                and permission in RolePermission[employee.role.name].value
            )
        except KeyError:
            return False

    async def ensure_has_permission(
        self,
        user_id: UserId,
        permission: Permission,
        shop_id: ShopId | None = None,
    ) -> None:
        employee = await self._employee_reader.by_identity(user_id)

        if not self._has_permission(employee, permission, shop_id):
            raise AccessDeniedError()

    async def ensure_can_create_shop(self, user_id: UserId) -> None:
        await self.ensure_has_permission(user_id, Permission.CAN_CREATE_SHOP)

    async def ensure_can_edit_shop(
        self, user_id: UserId, shop_id: ShopId
    ) -> None:
        await self.ensure_has_permission(
            user_id, Permission.CAN_EDIT_SHOP, shop_id
        )

    async def ensure_can_delete_shop(
        self, user_id: UserId, shop_id: ShopId
    ) -> None:
        await self.ensure_has_permission(
            user_id, Permission.CAN_DELETE_SHOP, shop_id
        )

    async def ensure_can_create_employee(
        self,
        user_id: UserId,
        shop_id: ShopId,
    ) -> None:
        await self.ensure_has_permission(
            user_id, Permission.CAN_CREATE_EMPLOYEE, shop_id
        )

    async def ensure_can_edit_employee(
        self,
        user_id: UserId,
        shop_id: ShopId,
    ) -> None:
        await self.ensure_has_permission(
            user_id, Permission.CAN_EDIT_EMPLOYEE, shop_id
        )

    async def ensure_can_create_goods(
        self, user_id: UserId, shop_id: ShopId
    ) -> None:
        await self.ensure_has_permission(
            user_id, Permission.CAN_CREATE_GOODS, shop_id
        )
