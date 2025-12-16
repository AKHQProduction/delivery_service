import logging
from dataclasses import dataclass
from datetime import date

from backend.application.errors import AccessDeniedError, EntityNotFoundError
from backend.application.interfaces import IdentityProvider, ShopGateway
from backend.application.interfaces.gateways import Pagination
from backend.application.interfaces.gateways.order_gateway import (
    GetOrdersFilters,
    OrderGateway,
)
from backend.application.interfaces.pdf_generator import OrdersPDFGenerator

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ExportOrdersPDFQuery:
    delivery_date: date


class ExportOrdersPDFQueryHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        order_gateway: OrderGateway,
        shop_gateway: ShopGateway,
        pdf_generator: OrdersPDFGenerator,
    ) -> None:
        self._idp = idp
        self._order_gateway = order_gateway
        self._shop_gateway = shop_gateway
        self._pdf_generator = pdf_generator

    async def handle(self, query: ExportOrdersPDFQuery) -> bytes:
        logger.info("Exporting orders PDF for date: %s", query.delivery_date)

        current_user = await self._idp.current_user()

        shop_id = current_user.shop_id
        if not shop_id:
            logger.warning("User %s has no shop_id", current_user.user_id)
            raise AccessDeniedError

        shop_name = await self._shop_gateway.get_shop_name(shop_id)
        if not shop_name:
            logger.warning("Shop not found: shop_id=%s", shop_id)
            raise EntityNotFoundError(entity="Shop")

        filters = GetOrdersFilters(
            shop_id=shop_id,
            delivery_date=query.delivery_date,
        )
        pagination = Pagination(limit=1000, offset=0)

        orders = await self._order_gateway.read_all(filters, pagination)

        logger.info(
            "Found %d orders for date %s, shop %s",
            len(orders),
            query.delivery_date,
            shop_id,
        )

        pdf_bytes = self._pdf_generator.handle(
            orders=orders,
            delivery_date=query.delivery_date,
            shop_name=shop_name,
        )

        logger.info(
            "Successfully generated PDF for date %s, shop %s (%d bytes)",
            query.delivery_date,
            shop_id,
            len(pdf_bytes),
        )

        return pdf_bytes
