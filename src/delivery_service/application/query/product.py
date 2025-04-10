import logging
from collections.abc import Sequence
from dataclasses import dataclass

from bazario.asyncio import RequestHandler

from delivery_service.application.common.markers.requests import (
    TelegramRequest,
)
from delivery_service.application.ports.idp import IdentityProvider
from delivery_service.application.query.ports.product_gateway import (
    ProductGateway,
    ProductGatewayFilters,
    ProductReadModel,
)
from delivery_service.domain.shared.errors import AccessDeniedError
from delivery_service.domain.staff.repository import StaffMemberRepository

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GetAllProductsResponse:
    products: Sequence[ProductReadModel]
    total: int


@dataclass(frozen=True)
class GetAllProductsRequest(TelegramRequest[GetAllProductsResponse]):
    pass


class GetAllProductsHandler(
    RequestHandler[GetAllProductsRequest, GetAllProductsResponse]
):
    def __init__(
        self,
        idp: IdentityProvider,
        staff_repository: StaffMemberRepository,
        product_gateway: ProductGateway,
    ) -> None:
        self._idp = idp
        self._staff_repository = staff_repository
        self._product_gateway = product_gateway

    async def handle(
        self, request: GetAllProductsRequest
    ) -> GetAllProductsResponse:
        logger.info("Request to get all products")
        current_user_id = await self._idp.get_current_user_id()

        staff_member = await self._staff_repository.load_with_identity(
            user_id=current_user_id
        )
        if not staff_member:
            raise AccessDeniedError()

        filters = ProductGatewayFilters(shop_id=staff_member.from_shop)
        products = await self._product_gateway.read_all_products(
            filters=filters
        )
        total = await self._product_gateway.total(filters=filters)

        return GetAllProductsResponse(products=products, total=total)
