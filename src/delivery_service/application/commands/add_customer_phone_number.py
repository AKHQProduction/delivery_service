# ruff: noqa: E501
import logging
from dataclasses import dataclass

from bazario.asyncio import RequestHandler

from delivery_service.application.common.errors import (
    CustomerNotFoundError,
    EntityAlreadyExistsError,
    ShopNotFoundError,
)
from delivery_service.application.common.factories.phone_factory import (
    PhoneNumberFactory,
)
from delivery_service.application.common.markers.requests import (
    TelegramRequest,
)
from delivery_service.application.ports.idp import IdentityProvider
from delivery_service.domain.customer_registries.customer_registry_repository import (
    CustomerRegistryRepository,
)
from delivery_service.domain.customers.customer_id import CustomerID
from delivery_service.domain.customers.repository import CustomerRepository

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AddCustomerPhoneNumberRequest(TelegramRequest):
    customer_id: CustomerID
    new_phone_number: str


class AddCustomerPhoneNumberHandler(
    RequestHandler[AddCustomerPhoneNumberRequest, None]
):
    def __init__(
        self,
        idp: IdentityProvider,
        customer_registry_repository: CustomerRegistryRepository,
        customer_repository: CustomerRepository,
        phone_number_factory: PhoneNumberFactory,
    ) -> None:
        self._idp = idp
        self._customer_registry_repository = customer_registry_repository
        self._repository = customer_repository
        self._phone_number_factory = phone_number_factory

    async def handle(self, request: AddCustomerPhoneNumberRequest) -> None:
        logger.info("Request to add new phone number to customer")
        current_user_id = await self._idp.get_current_user_id()

        customer_registry = (
            await self._customer_registry_repository.load_with_identity(
                current_user_id
            )
        )
        if not customer_registry:
            raise ShopNotFoundError()

        customer = await self._repository.load_with_id(
            customer_id=request.customer_id
        )
        if not customer:
            raise CustomerNotFoundError()

        if await self._repository.exists_with_number(
            customer_registry.id, request.new_phone_number
        ):
            raise EntityAlreadyExistsError()

        new_phone_number = self._phone_number_factory.create_phone_number(
            number=request.new_phone_number,
            customer_id=customer.entity_id,
            shop_id=customer_registry.id,
        )

        customer_registry.add_phone_number_to_customer(
            customer, new_phone_number, current_user_id
        )
