# ruff: noqa: E501

import logging
from dataclasses import dataclass

from bazario.asyncio import RequestHandler

from delivery_service.application.common.errors import (
    CustomerNotFoundError,
    ShopNotFoundError,
)
from delivery_service.application.common.markers.requests import (
    TelegramRequest,
)
from delivery_service.application.ports.idp import IdentityProvider
from delivery_service.domain.customer_registries.customer_registry_repository import (
    CustomerRegistryRepository,
)
from delivery_service.domain.customers.repository import CustomerRepository
from delivery_service.domain.shared.user_id import UserID
from delivery_service.domain.shared.vo.address import (
    AddressData,
    CoordinatesData,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EditCustomerNameRequest(TelegramRequest[None]):
    customer_id: UserID
    new_name: str


class EditCustomerNameHandler(RequestHandler[EditCustomerNameRequest, None]):
    def __init__(
        self,
        idp: IdentityProvider,
        customer_registry_repository: CustomerRegistryRepository,
        customer_repository: CustomerRepository,
    ) -> None:
        self._idp = idp
        self._customer_registry_repository = customer_registry_repository
        self._repository = customer_repository

    async def handle(self, request: EditCustomerNameRequest) -> None:
        logger.info("Request to edit customer name %s", request.customer_id)
        current_user_id = await self._idp.get_current_user_id()

        customer_registry = (
            await self._customer_registry_repository.load_with_identity(
                current_user_id
            )
        )
        if not customer_registry:
            raise ShopNotFoundError()

        customer = await self._repository.load_with_id(request.customer_id)
        if not customer:
            raise CustomerNotFoundError()

        customer_registry.edit_customer_full_name(
            customer, current_user_id, request.new_name
        )
        logger.info(
            "Successfully edited customer name %s", request.customer_id
        )


@dataclass(frozen=True)
class EditCustomerPrimaryPhoneRequest(TelegramRequest[None]):
    customer_id: UserID
    new_phone: str


class EditCustomerPrimaryPhoneHandler(
    RequestHandler[EditCustomerPrimaryPhoneRequest, None]
):
    def __init__(
        self,
        idp: IdentityProvider,
        customer_registry_repository: CustomerRegistryRepository,
        customer_repository: CustomerRepository,
    ) -> None:
        self._idp = idp
        self._customer_registry_repository = customer_registry_repository
        self._repository = customer_repository

    async def handle(self, request: EditCustomerPrimaryPhoneRequest) -> None:
        logger.info("Request to edit customer phone %s", request.customer_id)
        current_user_id = await self._idp.get_current_user_id()

        customer_registry = (
            await self._customer_registry_repository.load_with_identity(
                current_user_id
            )
        )
        if not customer_registry:
            raise ShopNotFoundError()

        customer = await self._repository.load_with_id(request.customer_id)
        if not customer:
            raise CustomerNotFoundError()

        customer_registry.edit_customer_primary_phone(
            customer, current_user_id, request.new_phone
        )
        logger.info(
            "Successfully edited customer phone %s", request.customer_id
        )


@dataclass(frozen=True)
class EditCustomerAddressRequest(TelegramRequest[None]):
    customer_id: UserID
    address_data: AddressData
    coordinates: CoordinatesData


class EditCustomerAddressHandler(
    RequestHandler[EditCustomerAddressRequest, None]
):
    def __init__(
        self,
        idp: IdentityProvider,
        customer_registry_repository: CustomerRegistryRepository,
        customer_repository: CustomerRepository,
    ) -> None:
        self._idp = idp
        self._customer_registry_repository = customer_registry_repository
        self._repository = customer_repository

    async def handle(self, request: EditCustomerAddressRequest) -> None:
        logger.info("Request to edit customer address %s", request.customer_id)
        current_user_id = await self._idp.get_current_user_id()

        customer_registry = (
            await self._customer_registry_repository.load_with_identity(
                current_user_id
            )
        )
        if not customer_registry:
            raise ShopNotFoundError()

        customer = await self._repository.load_with_id(request.customer_id)
        if not customer:
            raise CustomerNotFoundError()

        customer_registry.edit_customer_address(
            customer,
            current_user_id,
            request.address_data,
            request.coordinates,
        )
        logger.info(
            "Successfully edited customer address %s", request.customer_id
        )
