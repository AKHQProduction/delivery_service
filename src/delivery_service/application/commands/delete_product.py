import logging
from dataclasses import dataclass

from bazario.asyncio import RequestHandler

from delivery_service.application.common.errors import ProductNotFoundError
from delivery_service.application.common.markers.requests import (
    TelegramRequest,
)
from delivery_service.application.ports.idp import IdentityProvider
from delivery_service.domain.products.access_service import (
    ProductAccessService,
)
from delivery_service.domain.products.product import ProductID
from delivery_service.domain.products.repository import ProductRepository
from delivery_service.domain.shared.errors import AccessDeniedError
from delivery_service.domain.staff.repository import StaffMemberRepository

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DeleteProductRequest(TelegramRequest[None]):
    product_id: ProductID


class DeleteProductHandler(RequestHandler[DeleteProductRequest, None]):
    def __init__(
        self,
        idp: IdentityProvider,
        staff_repository: StaffMemberRepository,
        product_repository: ProductRepository,
        access_service: ProductAccessService,
    ) -> None:
        self._idp = idp
        self._staff_repository = staff_repository
        self._product_repository = product_repository
        self._access_service = access_service

    async def handle(self, request: DeleteProductRequest) -> None:
        logger.info("Request to delete product")
        current_user_id = await self._idp.get_current_user_id()

        staff_member = await self._staff_repository.load_with_identity(
            user_id=current_user_id
        )
        if not staff_member:
            raise AccessDeniedError()
        product = await self._product_repository.load_with_id(
            request.product_id
        )
        if not product:
            raise ProductNotFoundError()

        self._access_service.can_delete_product(staff_member, product)
        await self._product_repository.delete(product)
