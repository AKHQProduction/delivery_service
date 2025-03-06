from dataclasses import dataclass

from bazario import Request
from bazario.asyncio import RequestHandler

from delivery_service.shared.application.ports.idp import IdentityProvider
from delivery_service.shared.application.ports.transaction_manager import (
    TransactionManager,
)
from delivery_service.shared.domain.identity_id import UserID
from delivery_service.shop_management.application.errors import (
    EmployeeNotFoundError,
    ShopNotFoundError,
)
from delivery_service.shop_management.domain.repository import (
    EmployeeRepository,
    ShopRepository,
)


@dataclass(frozen=True)
class DiscardEmployeeRequest(Request[None]):
    employee_id: UserID


class DiscardEmployeeHandler(RequestHandler[DiscardEmployeeRequest, None]):
    def __init__(
        self,
        identity_provider: IdentityProvider,
        shop_repository: ShopRepository,
        employee_repository: EmployeeRepository,
        transaction_manager: TransactionManager,
    ) -> None:
        self._identity_provider = identity_provider
        self._shop_repository = shop_repository
        self._employee_repository = employee_repository
        self._transaction_manager = transaction_manager

    async def handle(self, request: DiscardEmployeeRequest) -> None:
        current_user_id = await self._identity_provider.get_current_user_id()

        shop = await self._shop_repository.load_with_identity(current_user_id)
        if not shop:
            raise ShopNotFoundError()
        employee = await self._employee_repository.load_with_id(
            request.employee_id
        )
        if not employee:
            raise EmployeeNotFoundError()

        shop.discard_employee(employee=employee, firer_id=current_user_id)

        await self._employee_repository.delete(employee)
        await self._transaction_manager.commit()
