from application.common.identity_provider import IdentityProvider
from application.employee.gateway import EmployeeReader
from application.user.gateway import UserReader
from entities.employee.models import EmployeeRole
from entities.user.models import User, UserId


class TgIdentityProvider(IdentityProvider):
    def __init__(
        self,
        user_id: int,
        user_gateway: UserReader,
        employee_gateway: EmployeeReader,
    ):
        self._user_id = user_id
        self._user_gateway = user_gateway
        self._employee_gateway = employee_gateway

    async def get_user(self) -> User:
        return await self._user_gateway.by_id(UserId(self._user_id))

    async def get_role(self) -> EmployeeRole:
        employee = await self._employee_gateway.by_identity(
            UserId(self._user_id)
        )

        return employee.role
