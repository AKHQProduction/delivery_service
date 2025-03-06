from dataclasses import dataclass

from bazario import Request
from bazario.asyncio import RequestHandler

from delivery_service.shared.application.ports.idp import IdentityProvider
from delivery_service.shared.application.ports.transaction_manager import (
    TransactionManager,
)
from delivery_service.shop_managment.domain.employee import EmployeeRole
from delivery_service.shop_managment.domain.factory import (
    DaysOffData,
    ShopFactory,
)
from delivery_service.shop_managment.domain.repository import (
    ShopRepository,
)
from delivery_service.shop_managment.domain.shop import ShopID


@dataclass(frozen=True)
class CreateNewShopRequest(Request[ShopID]):
    shop_name: str
    shop_location: str
    days_off: DaysOffData


class CreateNewShopHandler(RequestHandler[CreateNewShopRequest, ShopID]):
    def __init__(
        self,
        identity_provider: IdentityProvider,
        shop_factory: ShopFactory,
        shop_repository: ShopRepository,
        transaction_manager: TransactionManager,
    ) -> None:
        self._idp = identity_provider
        self._factory = shop_factory
        self._repository = shop_repository
        self._transaction_manager = transaction_manager

    async def handle(self, request: CreateNewShopRequest) -> ShopID:
        current_user_id = await self._idp.get_current_user_id()

        new_shop = await self._factory.create_shop(
            request.shop_name,
            request.shop_location,
            request.days_off,
            current_user_id,
        )
        self._repository.add(new_shop)
        new_shop.add_employee(
            employee_id=current_user_id,
            role=EmployeeRole.SHOP_OWNER,
            hirer=current_user_id,
        )

        await self._transaction_manager.commit()

        return new_shop.entity_id
