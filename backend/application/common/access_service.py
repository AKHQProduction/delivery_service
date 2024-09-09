from application.common.identity_provider import IdentityProvider
from application.employee.gateway import EmployeeReader
from application.errors.access import AccessDeniedError
from entities.employee.models import EmployeeRole
from entities.shop.models import ShopId
from entities.user.models import User


class AccessService:
    def __init__(
            self,
            employee_reader: EmployeeReader,
            identity_provider: IdentityProvider
    ) -> None:
        self._employee_reader = employee_reader
        self._identity_provider = identity_provider

    async def _is_shop_owner(
            self,
            shop_id: ShopId
    ) -> bool:
        actor = await self._identity_provider.get_user()
        employee = await self._employee_reader.by_identity(actor.user_id)

        return (
                employee.role == EmployeeRole.ADMIN
                and
                employee.shop_id == shop_id
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
            shop_id: ShopId
    ) -> None:
        if not await self._is_shop_owner(shop_id):
            raise AccessDeniedError()

    async def ensure_can_create_employee(
            self,
            shop_id: ShopId,
    ) -> None:
        if not await self._is_shop_owner(shop_id):
            raise AccessDeniedError()

    async def ensure_can_edit_employee(
            self,
            shop_id: ShopId,
    ) -> None:
        if not await self._is_shop_owner(shop_id):
            raise AccessDeniedError()
