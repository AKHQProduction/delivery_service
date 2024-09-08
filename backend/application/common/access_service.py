from application.employee.gateway import EmployeeReader
from application.errors.access import AccessDeniedError
from application.specs.has_role import HasRoleSpec
from entities.employee.models import Employee, EmployeeRole
from entities.shop.models import Shop
from entities.user.models import User


class AccessService:
    def __init__(
            self,
            employee_reader: EmployeeReader
    ) -> None:
        self._employee_reader = employee_reader

    async def _is_shop_owner(
            self,
            shop: Shop,
            actor: User
    ) -> bool:
        employee = await self._employee_reader.by_identity(actor.user_id)

        return (
                employee.role == EmployeeRole.ADMIN
                and
                employee.shop_id == shop.shop_id
        )

    async def ensure_can_create_shop(
            self,
            user: User
    ) -> None:
        employee = await self._employee_reader.by_identity(user.user_id)

        if employee:
            raise AccessDeniedError()

    async def ensure_can_edit_shop(
            self,
            shop: Shop,
            actor: User
    ) -> None:
        if not self._is_shop_owner(shop, actor):
            raise AccessDeniedError()

    async def ensure_can_create_employee(
            self,
            shop: Shop,
            actor: User
    ) -> None:
        if not await self._is_shop_owner(shop, actor):
            raise AccessDeniedError()
