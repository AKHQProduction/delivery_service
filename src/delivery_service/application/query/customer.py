# ruff: noqa: E501
import logging
from collections.abc import Sequence
from dataclasses import dataclass

from bazario.asyncio import RequestHandler

from delivery_service.application.common.markers.requests import (
    TelegramRequest,
)
from delivery_service.application.ports.idp import IdentityProvider
from delivery_service.application.query.ports.customer_gateway import (
    CustomerGateway,
    CustomerGatewayFilters,
    CustomerReadModel,
)
from delivery_service.domain.customer_registries.customer_registry_repository import (
    CustomerRegistryRepository,
)
from delivery_service.domain.shared.errors import AccessDeniedError

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GetAllCustomersResponse:
    customers: Sequence[CustomerReadModel]
    total: int


@dataclass(frozen=True)
class GetAllCustomersRequest(TelegramRequest[GetAllCustomersResponse]):
    pass


class GetAllCustomersHandler(
    RequestHandler[GetAllCustomersRequest, GetAllCustomersResponse]
):
    def __init__(
        self,
        idp: IdentityProvider,
        customer_registry_repository: CustomerRegistryRepository,
        customer_gateway: CustomerGateway,
    ) -> None:
        self._idp = idp
        self._customer_registry_repository = customer_registry_repository
        self._customer_gateway = customer_gateway

    async def handle(
        self, request: GetAllCustomersRequest
    ) -> GetAllCustomersResponse:
        logger.info("Request to get all customers")
        current_user_id = await self._idp.get_current_user_id()

        customer_registry = (
            await self._customer_registry_repository.load_with_identity(
                identity_id=current_user_id
            )
        )
        if not customer_registry:
            raise AccessDeniedError()

        filters = CustomerGatewayFilters(shop_id=customer_registry.id)
        customers = await self._customer_gateway.read_all_customers(
            filters=filters
        )
        total = await self._customer_gateway.total(filters=filters)

        return GetAllCustomersResponse(customers=customers, total=total)
