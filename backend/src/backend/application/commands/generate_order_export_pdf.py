import asyncio
import logging
from dataclasses import dataclass
from datetime import date

from backend.application.errors import AccessDeniedError, EntityNotFoundError
from backend.application.interfaces.gateways import Pagination
from backend.application.interfaces.gateways.order_gateway import (
    GetOrdersFilters,
    OrderReadModel,
)
from backend.infrastructure.idp import TelegramIdentityProvider
from backend.infrastructure.pdf import ReportLabOrdersPDFGenerator
from backend.infrastructure.persistence.gateways import (
    RedisPDFStorage,
    SQLAlchemyOrderGateway,
    SQLAlchemyShopGateway,
)

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
        idp: TelegramIdentityProvider,
        order_gateway: SQLAlchemyOrderGateway,
        shop_gateway: SQLAlchemyShopGateway,
        pdf_generator: ReportLabOrdersPDFGenerator,
        pdf_storage: RedisPDFStorage,
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
            start_date=command.delivery_date,
            end_date=command.delivery_date,
        )

        batch_size = 200
        offset = 0
        orders: list[OrderReadModel] = []

        while True:
            pagination = Pagination(limit=batch_size, offset=offset)
            batch = await self._order_gateway.read_all(filters, pagination)
            orders.extend(batch)
            if len(batch) < batch_size:
                break
            offset += batch_size

        logger.info(
            "Found %d orders for date %s, shop %s",
            len(orders),
            command.delivery_date,
            shop_id,
        )

        loop = asyncio.get_running_loop()
        pdf_bytes = await loop.run_in_executor(
            None,
            self._pdf_generator.handle,
            orders,
            command.delivery_date,
            shop_name,
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
