# ruff: noqa: E501

import logging
from dataclasses import dataclass

from bazario.asyncio import RequestHandler

from delivery_service.application.common.errors import (
    EntityAlreadyExistsError,
    ShopNotFoundError,
)
from delivery_service.application.common.markers.requests import (
    TelegramRequest,
)
from delivery_service.application.ports.id_generator import IDGenerator
from delivery_service.application.ports.idp import IdentityProvider
from delivery_service.domain.customer_registries.customer_registry import (
    AddressData,
    CoordinatesData,
    DeliveryAddressData,
)
from delivery_service.domain.customer_registries.customer_registry_repository import (
    CustomerRegistryRepository,
)
from delivery_service.domain.customers.repository import CustomerRepository

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AddNewCustomerRequest(TelegramRequest):
    full_name: str
    phone_number: str
    address_data: AddressData
    coordinates: CoordinatesData


class AddNewCustomerHandler(RequestHandler[AddNewCustomerRequest, None]):
    def __init__(
        self,
        idp: IdentityProvider,
        id_generator: IDGenerator,
        customer_registry_repository: CustomerRegistryRepository,
        customer_repository: CustomerRepository,
    ) -> None:
        self._idp = idp
        self._id_generator = id_generator
        self._customer_registry_repository = customer_registry_repository
        self._repository = customer_repository

    async def handle(self, request: AddNewCustomerRequest) -> None:
        logger.info("Request to add new customer")
        current_user_id = await self._idp.get_current_user_id()

        if await self._repository.exists(request.phone_number):
            raise EntityAlreadyExistsError()

        customer_registry = (
            await self._customer_registry_repository.load_with_identity(
                current_user_id
            )
        )
        if not customer_registry:
            raise ShopNotFoundError()

        new_customer_id = self._id_generator.generate_user_id()
        new_customer = customer_registry.add_new_customer(
            new_customer_id=new_customer_id,
            full_name=request.full_name,
            primary_phone_number=request.phone_number,
            delivery_data=DeliveryAddressData(
                coordinates=request.coordinates, address=request.address_data
            ),
            creator_id=current_user_id,
        )
        self._repository.add(new_customer)
