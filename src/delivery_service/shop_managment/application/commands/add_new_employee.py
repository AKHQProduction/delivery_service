from dataclasses import dataclass

from bazario import Request
from bazario.asyncio import RequestHandler

from delivery_service.shared.application.ports.idp import IdentityProvider
from delivery_service.shared.application.ports.transaction_manager import (
    TransactionManager,
)
from delivery_service.shared.domain.identity_id import UserID
from delivery_service.shop_managment.application.errors import (
    ShopNotFoundError,
)
from delivery_service.shop_managment.domain.employee import EmployeeRole
from delivery_service.shop_managment.domain.repository import ShopRepository


@dataclass(frozen=True)
class AddNewEmployeeRequest(Request[None]):
    candidate_id: UserID
    role: EmployeeRole


class AddNewEmployeeHandler(RequestHandler[AddNewEmployeeRequest, None]):
    def __init__(
        self,
        identity_provider: IdentityProvider,
        shop_repository: ShopRepository,
        transaction_manager: TransactionManager,
    ) -> None:
        self._identity_provider = identity_provider
        self._shop_repository = shop_repository
        self._transaction_manager = transaction_manager

    async def handle(self, request: AddNewEmployeeRequest) -> None:
        current_user_id = await self._identity_provider.get_current_user_id()

        shop = await self._shop_repository.load_with_identity(current_user_id)
        if not shop:
            raise ShopNotFoundError()

        shop.add_employee(
            employee_id=request.candidate_id,
            role=request.role,
            hirer_id=current_user_id,
        )

        await self._transaction_manager.commit()
