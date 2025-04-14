import logging
from dataclasses import dataclass

from bazario.asyncio import RequestHandler

from delivery_service.application.common.errors import ShopNotFoundError
from delivery_service.application.common.factories.customer_factory import (
    CustomerFactory,
)
from delivery_service.application.common.markers.requests import (
    TelegramRequest,
)
from delivery_service.application.ports.idp import IdentityProvider
from delivery_service.domain.customers.repository import CustomerRepository
from delivery_service.domain.shops.repository import ShopRepository


@dataclass(frozen=True)
class AddNewCustomerRequest(TelegramRequest):
    full_name: str
    phone_number: str


class AddNewCustomerHandler(RequestHandler[AddNewCustomerRequest, None]):
    def __init__(
        self,
        idp: IdentityProvider,
        shop_repository: ShopRepository,
        customer_factory: CustomerFactory,
        customer_repository: CustomerRepository,
    ) -> None:
        self._idp = idp
        self._shop_repository = shop_repository
        self._factory = customer_factory
        self._repository = customer_repository

    async def handle(self, request: AddNewCustomerRequest) -> None:
        current_user_id = await self._idp.get_current_user_id()

        shop = await self._shop_repository.load_with_identity(current_user_id)
        if not shop:
            raise ShopNotFoundError()

        new_customer = self._factory.create_customer(
            shop_id=shop.entity_id,
            full_name=request.full_name,
            phone_number=request.phone_number,
        )
        logging.info(new_customer.entity_id)
        self._repository.add(new_customer)
