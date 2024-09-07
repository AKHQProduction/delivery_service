from application.employee.gateway import EmployeeReader
from application.errors.access import AccessDeniedError
from application.specs.has_role import HasRoleSpec
from entities.employee.models import EmployeeRole
from entities.shop.models import Shop
from entities.user.models import User


class AccessService:
    def __init__(self, employee_reader: EmployeeReader):
        self._employee_reader = employee_reader

    async def ensure_can_create_shop(self, user: User) -> None:
        employee = await self._employee_reader.by_identity(user.user_id)

        if employee:
            raise AccessDeniedError()

    async def ensure_can_edit_shop(
            self,
            shop: Shop,
            user: User
    ) -> None:
        employee = await self._employee_reader.by_identity(user.user_id)

        if (
                not HasRoleSpec(
                        EmployeeRole.ADMIN
                ).is_satisfied_by(
                        employee.role
                )
                or
                shop.shop_id != employee.shop_id
        ):
            raise AccessDeniedError()
