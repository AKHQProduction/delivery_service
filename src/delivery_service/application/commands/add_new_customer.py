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
from delivery_service.domain.customer_registries.customer_registry_repository import (
    CustomerRegistryRepository,
)
from delivery_service.domain.customers.repository import CustomerRepository
from delivery_service.domain.shared.dto import (
    AddressData,
    CoordinatesData,
    DeliveryAddressData,
)
from delivery_service.domain.shared.user_id import UserID

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AddNewCustomerRequest(TelegramRequest[UserID]):
    full_name: str
    phone_number: str
    address_data: AddressData
    coordinates: CoordinatesData


class AddNewCustomerHandler(RequestHandler[AddNewCustomerRequest, UserID]):
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

    async def handle(self, request: AddNewCustomerRequest) -> UserID:
        logger.info("Request to add new customer")
        current_user_id = await self._idp.get_current_user_id()

        customer_registry = (
            await self._customer_registry_repository.load_with_identity(
                current_user_id
            )
        )
        if not customer_registry:
            raise ShopNotFoundError()

        if await self._repository.exists(
            request.phone_number, customer_registry.id
        ):
            raise EntityAlreadyExistsError()

        new_customer_id = self._id_generator.generate_user_id()
        new_address_id = self._id_generator.generate_address_id()
        new_customer = customer_registry.add_new_customer(
            new_customer_id=new_customer_id,
            full_name=request.full_name,
            primary_phone_number=request.phone_number,
            address_id=new_address_id,
            delivery_data=DeliveryAddressData(
                coordinates=request.coordinates, address=request.address_data
            ),
            creator_id=current_user_id,
        )

        logger.info(new_customer)

        self._repository.add(new_customer)

        return new_customer_id
