import logging
from dataclasses import dataclass
from datetime import date, timedelta

from backend.application.common import ensure_exists
from backend.application.errors import (
    DateMustBeGreaterThanError,
    ProductIdRequiredForNewItemError,
)
from backend.application.policies.access import (
    ensure_can_manage,
    ensure_related_to_shop,
)
from backend.application.services.geocoder import Geocoder
from backend.application.services.order import (
    resolve_address,
    resolve_order_items,
    resolve_phone,
    update_order,
    update_order_items,
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
    today,
)
from backend.infrastructure.idp import IdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyClientGateway,
    SQLAlchemyOrderGateway,
    SQLAlchemyProductGateway,
    SQLAlchemyShopGateway,
    SQLAlchemyTimeSlotGateway,
)
from backend.infrastructure.persistence.tables.orders import Order
from backend.infrastructure.transaction_manager import TransactionManager

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EditOrderItem:
    quantity: int
    product_id: ProductId | None = None
    id: OrderItemId | None = None

    def __post_init__(self) -> None:
        if self.id is None and self.product_id is None:
            raise ProductIdRequiredForNewItemError


@dataclass(frozen=True)
class EditOrderCommand:
    order_id: OrderId
    client_id: ClientId | None = None
    delivery_date: date | None = None
    time_slot_id: TimeSlotId | None = None
    address_id: AddressId | None = None
    phone_id: PhoneId | None = None
    comment: str | Empty | None = None
    items: list[EditOrderItem] | None = None
    payment_method: PaymentMethod | None = None

    def __post_init__(self) -> None:
        if self.delivery_date is not None:
            current_date = today()
            if current_date > self.delivery_date:
                previous_date = current_date - timedelta(days=1)
                raise DateMustBeGreaterThanError(greater_than=previous_date)


class EditOrderCommandHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        client_gateway: SQLAlchemyClientGateway,
        product_gateway: SQLAlchemyProductGateway,
        order_gateway: SQLAlchemyOrderGateway,
        time_slot_gateway: SQLAlchemyTimeSlotGateway,
        shop_gateway: SQLAlchemyShopGateway,
        geocoder: Geocoder,
        tr_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._client_gateway = client_gateway
        self._product_gateway = product_gateway
        self._order_gateway = order_gateway
        self._time_slot_gateway = time_slot_gateway
        self._shop_gateway = shop_gateway
        self._geocoder = geocoder
        self._tr_manager = tr_manager

    async def handle(self, command: EditOrderCommand) -> None:
        current_user = await self._idp.current_user()
        ensure_can_manage(current_user)

        order = ensure_exists(
            await self._order_gateway.load_with_items(command.order_id),
            "Order",
        )
        ensure_related_to_shop(current_user, order.shop_id)

        logger.info(
            "Updating order %s for shop %s",
            command.order_id,
            current_user.shop_id,
        )

        client_id = None
        delivery_phone = None
        delivery_address = None

        if (
            command.client_id is not None
            or command.phone_id is not None
            or command.address_id is not None
        ):
            client_id_to_use = command.client_id or order.client_id
            client = ensure_exists(
                await self._client_gateway.load(client_id_to_use),
                "Client",
            )
            if command.client_id is not None:
                ensure_related_to_shop(current_user, client.shop_id)
                client_id = command.client_id
            if command.phone_id is not None:
                delivery_phone = resolve_phone(client, command.phone_id)
            if command.address_id is not None:
                delivery_address = resolve_address(client, command.address_id)
                if delivery_address.coordinates is None:
                    shop = await self._shop_gateway.load_shop(
                        current_user.shop_id
                    )
                    shop_city = shop.city if shop else None
                    coords = await self._geocoder.geocode_if_missing(
                        street=delivery_address.street,
                        house=delivery_address.house,
                        coordinates=None,
                        shop_city=shop_city,
                    )
                    if coords is not None:
                        delivery_address.coordinates = coords
                        addr_obj = next(
                            a
                            for a in client.addresses
                            if a.id == command.address_id
                        )
                        coords.apply_to(addr_obj)

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

        update_order(
            order,
            client_id=client_id,
            delivery_date=command.delivery_date,
            delivery_start_time=delivery_start_time,
            delivery_end_time=delivery_end_time,
            delivery_phone=delivery_phone,
            delivery_address=delivery_address,
            comment=command.comment,
            payment_method=command.payment_method,
        )

        if command.items is not None:
            await self._process_items(command, order)

        await self._tr_manager.commit()

        logger.info(
            "Successfully updated order: id=%s, shop_id=%s",
            command.order_id,
            order.shop_id,
        )

    async def _process_items(
        self,
        command: EditOrderCommand,
        order: Order,
    ) -> None:
        product_ids = {
            item.product_id
            for item in command.items  # type: ignore[union-attr]
            if item.product_id is not None
        }
        existing_product_ids = {
            item.product_id
            for item in order.items
            if item.product_id is not None
        }
        all_product_ids = list(product_ids | existing_product_ids)

        products = (
            await self._product_gateway.load_many(all_product_ids)
            if all_product_ids
            else []
        )
        for pid in product_ids:
            ensure_exists(
                next((p for p in products if p.id == pid), None),
                "Product",
            )

        item_dtos = resolve_order_items(
            items=[
                (item.id, item.quantity, item.product_id)
                for item in command.items  # type: ignore[union-attr]
            ],
            existing_items=order.items,
            products=products,
        )
        removed = update_order_items(order, item_dtos)
        await self._order_gateway.delete_items(removed)
