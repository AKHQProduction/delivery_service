import logging
from dataclasses import dataclass
from datetime import date, time, timedelta

from backend.application.common import ensure_exists
from backend.application.dto.coordinates import CoordinatesDTO
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
from backend.application.services.route_builder import (
    create_route_plan,
    insert_order_into_route,
)
from backend.application.services.tsp_solvers import RouteOptimizer
from backend.application.vars import (
    AddressId,
    ClientId,
    OrderId,
    PaymentMethod,
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
    SQLAlchemyRoutePlanGateway,
    SQLAlchemyShopGateway,
    SQLAlchemyTimeSlotGateway,
)
from backend.infrastructure.persistence.tables import (
    Order as OrderModel,
    Product,
)
from backend.infrastructure.transaction_manager import TransactionManager

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class OrderProductInput:
    product_id: ProductId
    quantity: int


@dataclass(frozen=True)
class CreateOrderCommand:
    client_id: ClientId
    delivery_date: date
    time_slot_id: TimeSlotId
    address_id: AddressId
    phone_id: PhoneId
    products: list[OrderProductInput]
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
        idp: IdentityProvider,
        client_gateway: SQLAlchemyClientGateway,
        product_gateway: SQLAlchemyProductGateway,
        order_gateway: SQLAlchemyOrderGateway,
        time_slot_gateway: SQLAlchemyTimeSlotGateway,
        shop_gateway: SQLAlchemyShopGateway,
        route_plan_gateway: SQLAlchemyRoutePlanGateway,
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
                require_house=False,
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

        await self._auto_insert_into_route(
            shop_id=current_user.shop_id,
            order=order,
            time_slot_id=command.time_slot_id,
            start_time=time_slot.start_time,
            end_time=time_slot.end_time,
        )

        await self._tr_manager.commit()

        return order_id

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
            await self._create_initial_route_plan(
                shop_id, order.date, time_slot_id, start_time, end_time
            )
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
            insert_order_into_route(route_plan, order, shop_coords, all_orders)
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
    ) -> None:
        existing_orders = await self._order_gateway.load_by_date(
            shop_id=shop_id,
            delivery_date=delivery_date,
            start_time=start_time,
            end_time=end_time,
        )
        if len(existing_orders) < 2:
            return

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

    async def _load_shop_coords(
        self, shop_id: ShopId
    ) -> CoordinatesDTO | None:
        shop = await self._shop_gateway.load_shop(shop_id)
        return CoordinatesDTO.build(
            shop.latitude if shop else None,
            shop.longitude if shop else None,
        )
