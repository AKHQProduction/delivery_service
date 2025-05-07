# ruff: noqa: E501

import logging
from dataclasses import dataclass

from bazario.asyncio import RequestHandler

from delivery_service.application.common.errors import (
    EntityAlreadyExistsError,
    ShopNotFoundError,
)
from delivery_service.application.common.factories.address_factory import (
    AddressFactory,
)
from delivery_service.application.common.factories.phone_factory import (
    PhoneNumberFactory,
)
from delivery_service.application.common.markers.requests import (
    TelegramRequest,
)
from delivery_service.application.ports.id_generator import IDGenerator
from delivery_service.application.ports.idp import IdentityProvider
from delivery_service.domain.customer_registries.customer_registry_repository import (
    CustomerRegistryRepository,
)
from delivery_service.domain.customers.customer_id import CustomerID
from delivery_service.domain.customers.repository import CustomerRepository
from delivery_service.domain.shared.dto import (
    AddressData,
    CoordinatesData,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AddNewCustomerRequest(TelegramRequest[CustomerID]):
    name: str
    phone_number: str
    address_data: AddressData
    coordinates: CoordinatesData


class AddNewCustomerHandler(RequestHandler[AddNewCustomerRequest, CustomerID]):
    def __init__(
        self,
        idp: IdentityProvider,
        id_generator: IDGenerator,
        customer_registry_repository: CustomerRegistryRepository,
        customer_repository: CustomerRepository,
        address_factory: AddressFactory,
        phone_number_factory: PhoneNumberFactory,
    ) -> None:
        self._idp = idp
        self._id_generator = id_generator
        self._customer_registry_repository = customer_registry_repository
        self._repository = customer_repository
        self._address_factory = address_factory
        self._phone_number_factory = phone_number_factory

    async def handle(self, request: AddNewCustomerRequest) -> CustomerID:
        logger.info("Request to add new customer")
        current_user_id = await self._idp.get_current_user_id()

        customer_registry = (
            await self._customer_registry_repository.load_with_identity(
                current_user_id
            )
        )
        if not customer_registry:
            raise ShopNotFoundError()

        if await self._repository.exists_with_number(
            shop_id=customer_registry.id, phone_number=request.phone_number
        ):
            raise EntityAlreadyExistsError()

        new_customer_id = self._id_generator.generate_customer_id()

        address = self._address_factory.create_address(
            request.address_data,
            request.coordinates,
            new_customer_id,
            customer_registry.id,
        )
        phone_number = self._phone_number_factory.create_phone_number(
            number=request.phone_number,
            customer_id=new_customer_id,
            shop_id=customer_registry.id,
            is_primary=True,
        )
        new_customer = customer_registry.add_new_customer(
            new_customer_id=new_customer_id,
            name=request.name,
            primary_phone_number=phone_number,
            address=address,
            creator_id=current_user_id,
        )
        self._repository.add(new_customer)

        return new_customer_id
