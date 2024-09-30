from enum import Enum, auto
from typing import ClassVar

from application.employee.gateway import EmployeeReader
from application.errors.access import AccessDeniedError
from entities.employee.models import Employee
from entities.order.models import Order
from entities.shop.models import ShopId
from entities.user.models import UserId
from infrastructure.tg.config import ProjectConfig


class Permission(Enum):
    CAN_CREATE_SHOP = auto()
    CAN_EDIT_SHOP = auto()
    CAN_DELETE_SHOP = auto()
    CAN_CREATE_EMPLOYEE = auto()
    CAN_EDIT_EMPLOYEE = auto()
    CAN_CREATE_GOODS = auto()
    CAN_EDIT_GOODS = auto()
    CAN_DELETE_GOODS = auto()
    CAN_GET_ORDER = auto()
    CAN_EDIT_ORDER = auto()
    CAN_DElETE_ORDER = auto()


class RolePermission(Enum):
    ADMIN: ClassVar[set[Permission]] = {
        Permission.CAN_EDIT_SHOP,
        Permission.CAN_DELETE_SHOP,
        Permission.CAN_CREATE_EMPLOYEE,
        Permission.CAN_EDIT_EMPLOYEE,
        Permission.CAN_CREATE_GOODS,
        Permission.CAN_DELETE_GOODS,
        Permission.CAN_EDIT_GOODS,
        Permission.CAN_GET_ORDER,
        Permission.CAN_EDIT_ORDER,
        Permission.CAN_DElETE_ORDER,
    }
    MANAGER: ClassVar[set[Permission]] = {
        Permission.CAN_GET_ORDER,
        Permission.CAN_EDIT_ORDER,
        Permission.CAN_DElETE_ORDER,
    }
    DEFAULT: ClassVar[set[Permission]] = {
        Permission.CAN_CREATE_SHOP,
    }


class AccessService:
    def __init__(
        self, employee_reader: EmployeeReader, project_config: ProjectConfig
    ) -> None:
        self._employee_reader = employee_reader
        self._project_config = project_config

    def _is_superuser(self, user_id: UserId) -> None:
        if not user_id == self._project_config.admin_id:
            raise AccessDeniedError()

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

    async def _ensure_has_permission(
        self,
        user_id: UserId,
        permission: Permission,
        shop_id: ShopId | None = None,
    ) -> None:
        employee = await self._employee_reader.by_identity(user_id)

        if not self._has_permission(employee, permission, shop_id):
            raise AccessDeniedError()

    async def ensure_can_create_shop(self, user_id: UserId) -> None:
        await self._ensure_has_permission(user_id, Permission.CAN_CREATE_SHOP)

    def ensure_can_get_all_shop(self, user_id: UserId | None) -> None:
        self._is_superuser(user_id)

    async def ensure_can_edit_shop(
        self, user_id: UserId, shop_id: ShopId
    ) -> None:
        await self._ensure_has_permission(
            user_id, Permission.CAN_EDIT_SHOP, shop_id
        )

    async def ensure_can_delete_shop(
        self, user_id: UserId, shop_id: ShopId
    ) -> None:
        await self._ensure_has_permission(
            user_id, Permission.CAN_DELETE_SHOP, shop_id
        )

    async def ensure_can_create_employee(
        self,
        user_id: UserId,
        shop_id: ShopId,
    ) -> None:
        await self._ensure_has_permission(
            user_id, Permission.CAN_CREATE_EMPLOYEE, shop_id
        )

    async def ensure_can_edit_employee(
        self,
        user_id: UserId,
        shop_id: ShopId,
    ) -> None:
        await self._ensure_has_permission(
            user_id, Permission.CAN_EDIT_EMPLOYEE, shop_id
        )

    async def ensure_can_create_goods(
        self, user_id: UserId, shop_id: ShopId
    ) -> None:
        await self._ensure_has_permission(
            user_id, Permission.CAN_CREATE_GOODS, shop_id
        )

    async def ensure_can_edit_goods(
        self, user_id: UserId, shop_id: ShopId
    ) -> None:
        await self._ensure_has_permission(
            user_id, Permission.CAN_EDIT_GOODS, shop_id
        )

    async def ensure_can_delete_goods(
        self, user_id: UserId, shop_id: ShopId
    ) -> None:
        await self._ensure_has_permission(
            user_id, Permission.CAN_DELETE_GOODS, shop_id
        )

    async def ensure_can_get_order(
        self, user_id: UserId, order: Order
    ) -> None:
        await self._ensure_has_permission(
            user_id, Permission.CAN_GET_ORDER, order.shop_id
        ) or order.user_id == user_id

    async def ensure_can_edit_order(self, user_id: UserId, order: Order):
        await self._ensure_has_permission(
            user_id, Permission.CAN_EDIT_ORDER, order.shop_id
        ) or order.user_id == user_id

    async def ensure_can_delete_order(self, user_id: UserId, order: Order):
        await self._ensure_has_permission(
            user_id, Permission.CAN_EDIT_ORDER, order.shop_id
        ) or order.user_id == user_id
