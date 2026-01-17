import logging
from dataclasses import dataclass
from datetime import date

from backend.application.errors import AccessDeniedError, EntityNotFoundError
from backend.application.interfaces import (
    IdentityProvider,
    PDFStorage,
    ShopGateway,
)
from backend.application.interfaces.gateways import Pagination
from backend.application.interfaces.gateways.order_gateway import (
    GetOrdersFilters,
    OrderGateway,
)
from backend.application.interfaces.pdf_generator import OrdersPDFGenerator

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GenerateOrderExportPDFCommand:
    delivery_date: date


@dataclass(frozen=True)
class GenerateOrderExportPDFResult:
    file_id: str
    filename: str


class GenerateOrderExportPDFCommandHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        order_gateway: OrderGateway,
        shop_gateway: ShopGateway,
        pdf_generator: OrdersPDFGenerator,
        pdf_storage: PDFStorage,
    ) -> None:
        self._idp = idp
        self._order_gateway = order_gateway
        self._shop_gateway = shop_gateway
        self._pdf_generator = pdf_generator
        self._pdf_storage = pdf_storage

    async def handle(
        self, command: GenerateOrderExportPDFCommand
    ) -> GenerateOrderExportPDFResult:
        logger.info(
            "Generating orders PDF for date: %s", command.delivery_date
        )

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
            delivery_date=command.delivery_date,
        )
        pagination = Pagination(limit=1000, offset=0)

        orders = await self._order_gateway.read_all(filters, pagination)

        logger.info(
            "Found %d orders for date %s, shop %s",
            len(orders),
            command.delivery_date,
            shop_id,
        )

        pdf_bytes = self._pdf_generator.handle(
            orders=orders,
            delivery_date=command.delivery_date,
            shop_name=shop_name,
        )

        filename = f"orders_{command.delivery_date.isoformat()}.pdf"
        file_id = await self._pdf_storage.save(pdf_bytes, filename)

        logger.info(
            "Successfully generated PDF for date %s, shop %s (file_id=%s)",
            command.delivery_date,
            shop_id,
            file_id,
        )

        return GenerateOrderExportPDFResult(file_id=file_id, filename=filename)
