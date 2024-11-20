from application.common.identity_provider import IdentityProvider
from application.common.interfaces.user.gateways import UserGateway
from application.employee.gateway import EmployeeGateway
from application.user.errors import UserNotFoundError
from entities.employee.models import EmployeeRole
from entities.user.models import User


class TgIdentityProvider(IdentityProvider):
    def __init__(
        self,
        tg_id: int,
        user_mapper: UserGateway,
        employee_gateway: EmployeeGateway,
    ):
        self._tg_id = tg_id
        self._user_mapper = user_mapper
        self._employee_gateway = employee_gateway

    async def get_user(self) -> User | None:
        return await self._user_mapper.get_with_tg_id(self._tg_id)

    async def get_role(self) -> EmployeeRole | None:
        user = await self.get_user()
        if not user:
            raise UserNotFoundError()

        employee = await self._employee_gateway.by_identity(user.user_id)

        return None if not employee else employee.role
