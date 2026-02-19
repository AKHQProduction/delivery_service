from backend.application.dto.gateways.shop_gateway import (
    EmployeeReadModel,
)
from backend.application.errors import EntityNotFoundError
from backend.application.vars import UserId
from backend.infrastructure.idp import IdentityProvider
from backend.infrastructure.persistence.gateways import SQLAlchemyShopGateway


class GetEmployeeQueryHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        shop_gateway: SQLAlchemyShopGateway,
    ) -> None:
        self._idp = idp
        self._shop_gateway = shop_gateway

    async def handle(self, user_id: UserId) -> EmployeeReadModel:
        await self._idp.current_user()

        if employee := await self._shop_gateway.read_employee(user_id):
            return employee
        raise EntityNotFoundError(entity="Employee")
