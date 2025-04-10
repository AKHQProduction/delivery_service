# ruff: noqa: E501
import logging
from dataclasses import dataclass

from bazario.asyncio import RequestHandler

from delivery_service.application.common.factories.product_factory import (
    ProductFactory,
)
from delivery_service.application.common.markers.requests import (
    TelegramRequest,
)
from delivery_service.application.ports.id_generator import IDGenerator
from delivery_service.application.ports.idp import IdentityProvider
from delivery_service.domain.products.product import (
    ProductID,
    ProductType,
)
from delivery_service.domain.products.repository import (
    ProductRepository,
)
from delivery_service.domain.shared.errors import AccessDeniedError
from delivery_service.domain.shared.new_types import FixedDecimal
from delivery_service.domain.staff.repository import StaffMemberRepository

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AddNewProductRequest(TelegramRequest[ProductID]):
    title: str
    price: FixedDecimal
    product_type: ProductType


class AddNewProductHandler(RequestHandler[AddNewProductRequest, ProductID]):
    def __init__(
        self,
        identity_provider: IdentityProvider,
        product_factory: ProductFactory,
        id_generator: IDGenerator,
        product_repository: ProductRepository,
        staff_repository: StaffMemberRepository,
    ) -> None:
        self._idp = identity_provider
        self._product_factory = product_factory
        self._id_generator = id_generator
        self._product_repository = product_repository
        self._staff_repository = staff_repository

    async def handle(self, request: AddNewProductRequest) -> ProductID:
        logger.info("Request to add new product")
        current_user_id = await self._idp.get_current_user_id()

        staff_member = await self._staff_repository.load_with_identity(
            user_id=current_user_id
        )
        if not staff_member:
            raise AccessDeniedError()

        new_product = await self._product_factory.create_new_product(
            title=request.title,
            price=request.price,
            product_type=request.product_type,
            creator=staff_member,
        )
        self._product_repository.add(new_product)

        return new_product.entity_id
