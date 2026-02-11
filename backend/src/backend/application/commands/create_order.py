import logging
from dataclasses import dataclass
from datetime import date, timedelta

from backend.application.common import ensure_exists
from backend.application.errors import DateMustBeGreaterThanError
from backend.application.policies.access import (
    ensure_can_manage,
    ensure_related_to_shop,
)
from backend.application.services.geocoder import Geocoder
from backend.application.services.order import (
    create_order,
    create_order_item,
    resolve_address,
    resolve_phone,
)
from backend.application.vars import (
    AddressId,
    ClientId,
    OrderId,
    PaymentMethod,
    PhoneId,
    ProductId,
    TimeSlotId,
    today,
)
from backend.infrastructure.idp import TelegramIdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyClientGateway,
    SQLAlchemyOrderGateway,
    SQLAlchemyProductGateway,
    SQLAlchemyShopGateway,
    SQLAlchemyTimeSlotGateway,
)
from backend.infrastructure.persistence.tables import Product
from backend.infrastructure.transaction_manager import TransactionManager

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ProductDTO:
    product_id: ProductId
    quantity: int


@dataclass(frozen=True)
class CreateOrderCommand:
    client_id: ClientId
    delivery_date: date
    time_slot_id: TimeSlotId
    address_id: AddressId
    phone_id: PhoneId
    products: list[ProductDTO]
    payment_method: PaymentMethod
    comment: str | None = None

    def __post_init__(self) -> None:
        current_date = today()
        if current_date > self.delivery_date:
            previous_date = current_date - timedelta(days=1)

            raise DateMustBeGreaterThanError(greater_than=previous_date)


class CreateOrderCommandHandler:
    def __init__(
        self,
        idp: TelegramIdentityProvider,
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

    async def handle(self, command: CreateOrderCommand) -> OrderId:
        current_user = await self._idp.current_user()
        ensure_can_manage(current_user)

        logger.info(
            "Creating new order for shop %s with client %s",
            current_user.shop_id,
            command.client_id,
        )

        client = ensure_exists(
            await self._client_gateway.load(command.client_id),
            "Client",
        )
        ensure_related_to_shop(current_user, client.shop_id)

        delivery_phone = resolve_phone(client, command.phone_id)
        delivery_address = resolve_address(client, command.address_id)

        time_slot = ensure_exists(
            await self._time_slot_gateway.load(command.time_slot_id),
            "TimeSlot",
        )
        ensure_related_to_shop(current_user, time_slot.shop_id)

        product_ids = [p.product_id for p in command.products]
        loaded_products = await self._product_gateway.load_many(product_ids)
        products_map = {p.id: p for p in loaded_products}

        for pid in product_ids:
            ensure_exists(
                products_map.get(pid),
                "Product",
            )

        products: list[tuple[Product, int]] = [
            (products_map[p.product_id], p.quantity) for p in command.products
        ]

        if delivery_address.coordinates is None:
            shop = await self._shop_gateway.load_shop(current_user.shop_id)
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
                    a for a in client.addresses if a.id == command.address_id
                )
                coords.apply_to(addr_obj)

        order_id = self._order_gateway.next_id()
        order = create_order(
            order_id=order_id,
            shop_id=current_user.shop_id,
            client_id=client.id,
            delivery_date=command.delivery_date,
            delivery_start_time=time_slot.start_time,
            delivery_end_time=time_slot.end_time,
            delivery_phone=delivery_phone,
            delivery_address=delivery_address,
            payment_method=command.payment_method,
            comment=command.comment,
        )

        order.items = [
            create_order_item(
                name=product[0].name,
                quantity=product[1],
                price_per_item=product[0].price,
                product_id=product[0].id,
            )
            for product in products
        ]

        self._order_gateway.save(order)
        await self._tr_manager.commit()

        return order_id
