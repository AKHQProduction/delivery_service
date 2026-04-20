import logging
from dataclasses import dataclass
from datetime import date, time, timedelta

from backend.application.common import ensure_exists
from backend.application.dto.coordinates import CoordinatesDTO
from backend.application.dto.idp import CurrentUserDTO
from backend.application.errors import DateMustBeGreaterThanError
from backend.application.policies.access import (
    ensure_can_manage,
    ensure_related_to_shop,
)
from backend.application.services.edge_preference_collector import (
    PREFERENCE_WINDOW_DAYS,
    build_preference_map,
)
from backend.application.services.geocoder import Geocoder
from backend.application.services.order import (
    create_order,
    create_order_item,
    resolve_address,
    resolve_phone,
)
from backend.application.services.order_payment import (
    apply_balance_payment,
)
from backend.application.services.payment_method import (
    is_balance_payment_method,
)
from backend.application.services.route_builder import (
    create_route_plan,
    insert_order_into_route,
)
from backend.application.services.tsp_solvers import RouteOptimizer
from backend.application.vars import (
    AddressId,
    ClientId,
    OrderId,
    PhoneId,
    ProductId,
    ShopId,
    TimeSlotId,
    today,
)
from backend.infrastructure.idp import IdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyClientGateway,
    SQLAlchemyOrderGateway,
    SQLAlchemyProductGateway,
    SQLAlchemyRouteEdgeHistoryGateway,
    SQLAlchemyRoutePlanGateway,
    SQLAlchemyShopGateway,
    SQLAlchemyTimeSlotGateway,
)
from backend.infrastructure.persistence.tables import (
    Order as OrderModel,
    Product,
)
from backend.infrastructure.persistence.tables.base import DeliveryAddressDTO
from backend.infrastructure.persistence.tables.clients import Client
from backend.infrastructure.persistence.tables.shops import (
    ShopDeliveryTimeSlot,
)
from backend.infrastructure.transaction_manager import TransactionManager

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class OrderProductInput:
    product_id: ProductId
    quantity: int


@dataclass(frozen=True)
class ResolvedDeliveryDetails:
    client: Client
    delivery_phone: str
    delivery_address: DeliveryAddressDTO


@dataclass(frozen=True)
class CreateOrderCommand:
    client_id: ClientId
    delivery_date: date
    time_slot_id: TimeSlotId
    address_id: AddressId
    phone_id: PhoneId
    products: list[OrderProductInput]
    payment_method: str
    comment: str | None = None

    def __post_init__(self) -> None:
        current_date = today()
        if current_date > self.delivery_date:
            previous_date = current_date - timedelta(days=1)

            raise DateMustBeGreaterThanError(greater_than=previous_date)


class CreateOrderCommandHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        client_gateway: SQLAlchemyClientGateway,
        product_gateway: SQLAlchemyProductGateway,
        order_gateway: SQLAlchemyOrderGateway,
        time_slot_gateway: SQLAlchemyTimeSlotGateway,
        shop_gateway: SQLAlchemyShopGateway,
        route_plan_gateway: SQLAlchemyRoutePlanGateway,
        route_edge_history_gateway: SQLAlchemyRouteEdgeHistoryGateway,
        route_optimizer: RouteOptimizer,
        geocoder: Geocoder,
        tr_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._client_gateway = client_gateway
        self._product_gateway = product_gateway
        self._order_gateway = order_gateway
        self._time_slot_gateway = time_slot_gateway
        self._shop_gateway = shop_gateway
        self._route_plan_gateway = route_plan_gateway
        self._edge_gateway = route_edge_history_gateway
        self._route_optimizer = route_optimizer
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

        delivery = await self._resolve_delivery_details(
            client_id=command.client_id,
            address_id=command.address_id,
            phone_id=command.phone_id,
            shop_id=current_user.shop_id,
            current_user=current_user,
        )
        time_slot = await self._load_time_slot(
            command.time_slot_id, current_user
        )
        products = await self._resolve_products(command.products)

        order_id = self._order_gateway.next_id()
        order = create_order(
            order_id=order_id,
            shop_id=current_user.shop_id,
            client_id=delivery.client.id,
            delivery_date=command.delivery_date,
            delivery_start_time=time_slot.start_time,
            delivery_end_time=time_slot.end_time,
            delivery_phone=delivery.delivery_phone,
            delivery_address=delivery.delivery_address,
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
        await self._tr_manager.flush()

        if is_balance_payment_method(name=order.payment_method):
            client_for_update = ensure_exists(
                await self._client_gateway.load_for_update(delivery.client.id),
                "Client",
            )
            apply_balance_payment(order, client_for_update)

        await self._auto_insert_into_route(
            shop_id=current_user.shop_id,
            order=order,
            time_slot_id=command.time_slot_id,
            start_time=time_slot.start_time,
            end_time=time_slot.end_time,
        )

        await self._tr_manager.commit()

        return order_id

    async def _resolve_delivery_details(
        self,
        *,
        client_id: ClientId,
        address_id: AddressId,
        phone_id: PhoneId,
        shop_id: ShopId,
        current_user: CurrentUserDTO,
    ) -> ResolvedDeliveryDetails:
        client = ensure_exists(
            await self._client_gateway.load(client_id),
            "Client",
        )
        ensure_related_to_shop(current_user, client.shop_id)

        delivery_address = resolve_address(client, address_id)
        if delivery_address.coordinates is None:
            shop = await self._shop_gateway.load_shop(shop_id)
            shop_city = shop.city if shop else None
            coords = await self._geocoder.geocode_if_missing(
                street=delivery_address.street,
                house=delivery_address.house,
                coordinates=None,
                shop_city=shop_city,
                require_house=False,
            )
            if coords is not None:
                delivery_address.coordinates = coords
                addr_obj = next(
                    address
                    for address in client.addresses
                    if address.id == address_id
                )
                coords.apply_to(addr_obj)

        return ResolvedDeliveryDetails(
            client=client,
            delivery_phone=resolve_phone(client, phone_id),
            delivery_address=delivery_address,
        )

    async def _load_time_slot(
        self,
        time_slot_id: TimeSlotId,
        current_user: CurrentUserDTO,
    ) -> ShopDeliveryTimeSlot:
        time_slot = ensure_exists(
            await self._time_slot_gateway.load(time_slot_id),
            "TimeSlot",
        )
        ensure_related_to_shop(current_user, time_slot.shop_id)
        return time_slot

    async def _resolve_products(
        self,
        products: list[OrderProductInput],
    ) -> list[tuple[Product, int]]:
        product_ids = [product.product_id for product in products]
        loaded_products = await self._product_gateway.load_many(product_ids)
        products_map = {product.id: product for product in loaded_products}

        for product_id in product_ids:
            ensure_exists(products_map.get(product_id), "Product")

        return [
            (products_map[product.product_id], product.quantity)
            for product in products
        ]

    async def _auto_insert_into_route(
        self,
        shop_id: ShopId,
        order: OrderModel,
        time_slot_id: TimeSlotId,
        start_time: time,
        end_time: time,
    ) -> None:
        route_plan = await self._route_plan_gateway.load_by_date(
            shop_id=shop_id,
            delivery_date=order.date,
            time_slot_id=time_slot_id,
        )

        if route_plan is None:
            created = await self._create_initial_route_plan(
                shop_id, order.date, time_slot_id, start_time, end_time
            )
            if created:
                logger.info(
                    "Created initial route plan for shop %s, date=%s, slot=%s",
                    shop_id,
                    order.date,
                    time_slot_id,
                )
        else:
            shop_coords = await self._load_shop_coords(shop_id)
            all_orders = await self._order_gateway.load_by_date(
                shop_id=shop_id,
                delivery_date=order.date,
                start_time=start_time,
                end_time=end_time,
            )
            pref_map = (
                build_preference_map(
                    await self._edge_gateway.load_preferences(
                        shop_id, PREFERENCE_WINDOW_DAYS
                    )
                )
                or None
            )
            insert_order_into_route(
                route_plan, order, shop_coords, all_orders, pref_map
            )
            logger.info(
                "Inserted order %s into existing route plan %s",
                order.id,
                route_plan.id,
            )

    async def _create_initial_route_plan(
        self,
        shop_id: ShopId,
        delivery_date: date,
        time_slot_id: TimeSlotId,
        start_time: time,
        end_time: time,
    ) -> bool:
        existing_orders = await self._order_gateway.load_by_date(
            shop_id=shop_id,
            delivery_date=delivery_date,
            start_time=start_time,
            end_time=end_time,
        )
        if not existing_orders:
            return False

        shop_coords = await self._load_shop_coords(shop_id)

        optimized_ids = None
        if shop_coords:
            optimized_ids = await self._route_optimizer.compute(
                shop_coords, existing_orders
            )

        create_route_plan(
            route_plan_gateway=self._route_plan_gateway,
            shop_id=shop_id,
            delivery_date=delivery_date,
            time_slot_id=time_slot_id,
            orders=existing_orders,
            optimized_ids=optimized_ids,
        )
        return True

    async def _load_shop_coords(
        self, shop_id: ShopId
    ) -> CoordinatesDTO | None:
        shop = await self._shop_gateway.load_shop(shop_id)
        return CoordinatesDTO.build(
            shop.latitude if shop else None,
            shop.longitude if shop else None,
        )
