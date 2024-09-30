from application.common.identity_provider import IdentityProvider
from entities.employee.models import EmployeeRole
from entities.user.models import User, UserId
from tests.mocks.gateways.employee import FakeEmployeeGateway
from tests.mocks.gateways.user import FakeUserGateway


class FakeIdentityProvider(IdentityProvider):
    def __init__(
        self,
        user_id: UserId,
        user_gateway: FakeUserGateway,
        employee_gateway: FakeEmployeeGateway,
    ):
        self.user_id = user_id
        self.user_gateway = user_gateway
        self.employee_gateway = employee_gateway

    async def get_user(self) -> User | None:
        return await self.user_gateway.by_id(self.user_id)

    async def get_role(self) -> EmployeeRole | None:
        employee = await self.employee_gateway.by_identity(self.user_id)

        if not employee:
            return None
        return employee.role
