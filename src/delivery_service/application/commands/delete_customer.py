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

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DeleteCustomerRequest(TelegramRequest[None]):
    customer_id: UserID


class DeleteCustomerHandler(RequestHandler[DeleteCustomerRequest, None]):
    def __init__(
        self,
        idp: IdentityProvider,
        customer_registry_repository: CustomerRegistryRepository,
        customer_repository: CustomerRepository,
    ) -> None:
        self._idp = idp
        self._customer_registry_repository = customer_registry_repository
        self._repository = customer_repository

    async def handle(self, request: DeleteCustomerRequest) -> None:
        logger.info("Request to delete customer %s", request.customer_id)
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

        customer_registry.can_delete_customer(customer, current_user_id)
        await self._repository.delete(customer)

        logger.info("Successfully delete customer %s", request.customer_id)
