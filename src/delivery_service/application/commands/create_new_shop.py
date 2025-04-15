# ruff: noqa: E501
import logging
from dataclasses import dataclass

from bazario.asyncio import RequestHandler

from delivery_service.application.common.factories.shop_factory import (
    CoordinatesData,
    DaysOffData,
    ShopFactory,
)
from delivery_service.application.common.markers.requests import (
    TelegramRequest,
)
from delivery_service.application.ports.idp import IdentityProvider
from delivery_service.domain.shared.shop_id import ShopID
from delivery_service.domain.shops.errors import ShopCreationNotAllowedError
from delivery_service.domain.shops.repository import (
    ShopRepository,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CreateNewShopRequest(TelegramRequest[ShopID]):
    shop_name: str
    shop_coordinates: CoordinatesData
    days_off: DaysOffData


class CreateNewShopHandler(RequestHandler[CreateNewShopRequest, ShopID]):
    def __init__(
        self,
        identity_provider: IdentityProvider,
        shop_factory: ShopFactory,
        shop_repository: ShopRepository,
    ) -> None:
        self._idp = identity_provider
        self._factory = shop_factory
        self._repository = shop_repository

    async def handle(self, request: CreateNewShopRequest) -> ShopID:
        logger.info("Request to create new shop")

        current_user_id = await self._idp.get_current_user_id()
        if await self._repository.exists(current_user_id):
            raise ShopCreationNotAllowedError(current_user_id)

        new_shop = await self._factory.create_shop(
            request.shop_name,
            request.shop_coordinates,
            request.days_off,
            current_user_id,
        )
        self._repository.add(new_shop)

        return new_shop.entity_id
