# ruff: noqa: E501

import logging
from dataclasses import dataclass

from bazario.asyncio import RequestHandler

from delivery_service.application.common.errors import (
    CustomerNotFoundError,
    EntityAlreadyExistsError,
    ShopNotFoundError,
)
from delivery_service.application.common.factories.address_factory import (
    AddressFactory,
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
from delivery_service.domain.shared.dto import AddressData, CoordinatesData

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AddAddressToCustomerRequest(TelegramRequest[None]):
    customer_id: CustomerID
    address_data: AddressData
    coordinates: CoordinatesData


class AddAddressToCustomerHandler(
    RequestHandler[AddAddressToCustomerRequest, None]
):
    def __init__(
        self,
        idp: IdentityProvider,
        id_generator: IDGenerator,
        customer_registry_repository: CustomerRegistryRepository,
        customer_repository: CustomerRepository,
        address_factory: AddressFactory,
    ) -> None:
        self._idp = idp
        self._id_generator = id_generator
        self._customer_registry_repository = customer_registry_repository
        self._repository = customer_repository
        self._address_factory = address_factory

    async def handle(self, request: AddAddressToCustomerRequest) -> None:
        logger.info("Request to add new address to customer")
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

        if await self._repository.exists_with_address(
            customer_id=request.customer_id,
            city=request.address_data.city,
            street=request.address_data.street,
            house_number=request.address_data.house_number,
        ):
            raise EntityAlreadyExistsError()

        new_address = self._address_factory.create_address(
            address_data=request.address_data,
            coordinates_data=request.coordinates,
            customer_id=request.customer_id,
            shop_id=customer_registry.id,
        )

        customer_registry.add_address_to_customer(
            customer, new_address, current_user_id
        )
