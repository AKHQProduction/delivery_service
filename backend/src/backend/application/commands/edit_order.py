import logging
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

from backend.application.errors import (
    DateMustBeGreaterThanError,
    EntityNotFoundError,
    ProductIdRequiredForNewItemError,
)
from backend.application.interfaces.gateways.order_gateway import (
    DeliveryAddressDTO,
    OrderItemDTO,
    UpdateOrderDTO,
)
from backend.application.interfaces.idp import CurrentUserDTO
from backend.application.policies.access import (
    ensure_can_manage,
    ensure_related_to_shop,
)
from backend.application.vars import (
    AddressId,
    ClientId,
    Empty,
    OrderId,
    OrderItemId,
    PaymentMethod,
    PhoneId,
    ProductId,
    TimeSlotId,
)
from backend.domain.services.common import ensure_exists
from backend.infrastructure.idp import TelegramIdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyClientGateway,
    SQLAlchemyOrderGateway,
    SQLAlchemyProductGateway,
    SQLAlchemyTimeSlotGateway,
)
from backend.infrastructure.persistence.tables.clients import Client
from backend.infrastructure.persistence.tables.orders import (
    Order as OrderORM,
)
from backend.infrastructure.transaction_manager import TransactionManager

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class OrderItem:
    quantity: int
    product_id: ProductId | None = None
    id: OrderItemId | None = None

    def __post_init__(self) -> None:
        if self.id is None and self.product_id is None:
            raise ProductIdRequiredForNewItemError


@dataclass(frozen=True)
class UpdateOrderCommand:
    order_id: OrderId
    client_id: ClientId | None = None
    delivery_date: date | None = None
    time_slot_id: TimeSlotId | None = None
    address_id: AddressId | None = None
    phone_id: PhoneId | None = None
    comment: str | Empty | None = None
    items: list[OrderItem] | None = None
    payment_method: PaymentMethod | None = None

    def __post_init__(self) -> None:
        if self.delivery_date is not None:
            today = datetime.now(UTC).date()
            if today > self.delivery_date:
                previous_date = today - timedelta(days=1)
                raise DateMustBeGreaterThanError(greater_than=previous_date)


class UpdateOrderCommandHandler:
    def __init__(
        self,
        idp: TelegramIdentityProvider,
        client_gateway: SQLAlchemyClientGateway,
        product_gateway: SQLAlchemyProductGateway,
        order_gateway: SQLAlchemyOrderGateway,
        time_slot_gateway: SQLAlchemyTimeSlotGateway,
        tr_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._client_gateway = client_gateway
        self._product_gateway = product_gateway
        self._order_gateway = order_gateway
        self._time_slot_gateway = time_slot_gateway
        self._tr_manager = tr_manager

    async def handle(self, command: UpdateOrderCommand) -> None:
        current_user = await self._idp.current_user()
        ensure_can_manage(current_user)

        order = ensure_exists(
            await self._order_gateway.load(command.order_id),
            "Order",
        )
        ensure_related_to_shop(current_user, order.shop_id)

        logger.info(
            "Updating order %s for shop %s",
            command.order_id,
            current_user.shop_id,
        )

        update_dto = await self._build_update_dto(command, order, current_user)

        await self._order_gateway.update(update_dto)
        await self._tr_manager.commit()

        logger.info(
            "Successfully updated order: id=%s, shop_id=%s",
            command.order_id,
            order.shop_id,
        )

    async def _build_update_dto(
        self,
        command: UpdateOrderCommand,
        order: OrderORM,
        current_user: CurrentUserDTO,
    ) -> UpdateOrderDTO:
        (
            client_id,
            delivery_phone,
            delivery_address,
        ) = await self._process_client_changes(command, order, current_user)

        delivery_start_time = None
        delivery_end_time = None
        if command.time_slot_id is not None:
            time_slot = ensure_exists(
                await self._time_slot_gateway.load(command.time_slot_id),
                "TimeSlot",
            )
            ensure_related_to_shop(current_user, time_slot.shop_id)
            delivery_start_time = time_slot.start_time
            delivery_end_time = time_slot.end_time

        items: list[OrderItemDTO] | None = None
        if command.items is not None:
            items = await self._process_items(
                command.order_id,
                command.items,  # type: ignore[arg-type]
            )
        return UpdateOrderDTO(
            order_id=command.order_id,
            client_id=client_id,
            delivery_date=command.delivery_date,
            delivery_start_time=delivery_start_time,
            delivery_end_time=delivery_end_time,
            delivery_phone=delivery_phone,
            delivery_address=delivery_address,
            comment=command.comment,
            items=items,
            payment_method=command.payment_method,
        )

    async def _process_client_changes(
        self,
        command: UpdateOrderCommand,
        order: OrderORM,
        current_user: CurrentUserDTO,
    ) -> tuple[ClientId | None, str | None, DeliveryAddressDTO | None]:
        client_id: ClientId | None = None
        delivery_phone: str | None = None
        delivery_address: DeliveryAddressDTO | None = None

        need_client_load = (
            command.client_id is not None
            or command.phone_id is not None
            or command.address_id is not None
        )

        if not need_client_load:
            return client_id, delivery_phone, delivery_address

        client_id_to_use = command.client_id or order.client_id
        client = ensure_exists(
            await self._client_gateway.load(client_id_to_use),
            "Client",
        )

        if command.client_id is not None:
            ensure_related_to_shop(current_user, client.shop_id)
            client_id = command.client_id

        if command.phone_id is not None:
            delivery_phone = self._get_phone_number(client, command.phone_id)

        if command.address_id is not None:
            delivery_address = self._get_delivery_address(
                client, command.address_id
            )

        return client_id, delivery_phone, delivery_address

    @staticmethod
    def _get_phone_number(client: Client, phone_id: PhoneId) -> str:
        phone = next(
            (p for p in client.phones if p.id == phone_id),
            None,
        )
        if not phone:
            raise EntityNotFoundError(entity="Phone")
        return phone.number

    @staticmethod
    def _get_delivery_address(
        client: Client, address_id: AddressId
    ) -> DeliveryAddressDTO:
        address = next(
            (a for a in client.addresses if a.id == address_id),
            None,
        )
        if not address:
            raise EntityNotFoundError(entity="Address")
        return DeliveryAddressDTO(
            street=address.street,
            house=address.house,
            apartment=address.apartment,
            entrance=address.entrance,
            floor=address.floor,
            intercom=address.intercom,
            comment=address.comment,
        )

    async def _process_items(
        self, order_id: OrderId, items: list[OrderItem]
    ) -> list[OrderItemDTO]:
        existing_items = await self._order_gateway.load_items(order_id)
        existing_items_map = {item.id: item for item in existing_items}

        product_ids_to_load: set[ProductId] = set()
        item_product_map: dict[int, ProductId] = {}

        for idx, item in enumerate(items):
            product_id_to_use: ProductId | None = None

            if item.product_id is not None:
                product_id_to_use = item.product_id
            elif item.id is not None:
                existing_item = existing_items_map.get(item.id)
                if existing_item and existing_item.product_id:
                    product_id_to_use = existing_item.product_id

            if product_id_to_use is not None:
                product_ids_to_load.add(product_id_to_use)
                item_product_map[idx] = product_id_to_use

        products_map: dict[ProductId, tuple[str, Decimal]] = {}
        if product_ids_to_load:
            products = await self._product_gateway.load_many(
                list(product_ids_to_load)
            )
            products_map = {p.id: (p.name, p.price) for p in products}

            for product_id in product_ids_to_load:
                ensure_exists(
                    products_map.get(product_id),
                    "Product",
                )

        result: list[OrderItemDTO] = []
        for idx, item in enumerate(items):
            product_id_to_use = item_product_map.get(idx)
            name: str | None = None
            price_per_item: Decimal | None = None

            if product_id_to_use is not None:
                name, price_per_item = products_map[product_id_to_use]

            result.append(
                OrderItemDTO(
                    quantity=item.quantity,
                    name=name,
                    price_per_item=price_per_item,
                    id=item.id,
                    product_id=product_id_to_use,
                )
            )

        return result
