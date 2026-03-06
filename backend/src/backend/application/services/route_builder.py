import logging
from datetime import date, time

from backend.application.dto.coordinates import CoordinatesDTO
from backend.application.dto.gateways.route_gateway import (
    RoutePointReadModel,
    RouteReadModel,
    RouteStatsReadModel,
)
from backend.application.services.edge_preference_collector import (
    PreferenceMap,
)
from backend.application.services.tsp_solvers import RouteOptimizer
from backend.application.vars import (
    OrderId,
    PaymentMethod,
    RoutePlanId,
    ShopId,
    TimeSlotId,
)
from backend.infrastructure.persistence.gateways.route_plan_gateway import (
    SQLAlchemyRoutePlanGateway,
)
from backend.infrastructure.persistence.gateways.time_slot_gateway import (
    SQLAlchemyTimeSlotGateway,
)
from backend.infrastructure.persistence.tables.orders import Order
from backend.infrastructure.persistence.tables.route_plans import RoutePlan

logger = logging.getLogger(__name__)


async def resolve_time_slot(
    time_slot_gateway: SQLAlchemyTimeSlotGateway,
    time_slot_id: TimeSlotId | None,
) -> tuple[str | None, time | None, time | None]:
    if not time_slot_id:
        return None, None, None
    ts = await time_slot_gateway.load(time_slot_id)
    if not ts:
        return None, None, None
    time_range = (
        f"{ts.start_time.strftime('%H:%M')}-{ts.end_time.strftime('%H:%M')}"
    )
    label = f"{ts.label} | {time_range}" if ts.label else time_range
    return label, ts.start_time, ts.end_time


def build_route_read_model(
    route_plan_id: RoutePlanId,
    delivery_date: str,
    time_slot: str | None,
    time_slot_id: TimeSlotId | None,
    ordered_orders: list[Order],
    unroutable_orders: list[Order],
) -> RouteReadModel:
    points = [
        _order_to_point(order, seq) for seq, order in enumerate(ordered_orders)
    ]
    unroutable = [
        _order_to_point(order, seq=-1) for order in unroutable_orders
    ]

    addresses = set()
    for order in ordered_orders:
        addr = order.delivery_address
        if addr:
            addresses.add(f"{addr.street} {addr.house}")

    stats = RouteStatsReadModel(
        total_orders=len(ordered_orders) + len(unroutable_orders),
        unique_addresses=len(addresses),
    )

    return RouteReadModel(
        route_plan_id=route_plan_id,
        delivery_date=delivery_date,
        time_slot=time_slot,
        time_slot_id=time_slot_id,
        points=points,
        unroutable_orders=unroutable,
        stats=stats,
    )


def sort_orders_by_sequence(
    orders: list[Order],
    order_sequence: list,
) -> tuple[list[Order], list[Order]]:
    orders_map = {order.id: order for order in orders}
    sequence_ids = set(order_sequence)

    ordered: list[Order] = []
    for oid in order_sequence:
        order = orders_map.pop(oid, None)
        if order:
            ordered.append(order)

    ordered.extend(order for order in orders if order.id not in sequence_ids)

    routable = []
    unroutable = []
    for order in ordered:
        addr = order.delivery_address
        if addr and addr.coordinates:
            routable.append(order)
        else:
            unroutable.append(order)

    return routable, unroutable


def split_orders_by_coords(
    orders: list[Order],
) -> tuple[list[Order], list[Order]]:
    routable = []
    unroutable = []
    for order in orders:
        addr = order.delivery_address
        if addr and addr.coordinates:
            routable.append(order)
        else:
            unroutable.append(order)
    return routable, unroutable


def create_route_plan(
    route_plan_gateway: SQLAlchemyRoutePlanGateway,
    shop_id: ShopId,
    delivery_date: date,
    time_slot_id: TimeSlotId | None,
    orders: list[Order],
    optimized_ids: list[OrderId] | None,
) -> RoutePlan:
    if optimized_ids:
        routable, unroutable = sort_orders_by_sequence(orders, optimized_ids)
    else:
        routable, unroutable = split_orders_by_coords(orders)

    all_ids = [o.id for o in routable] + [o.id for o in unroutable]

    route_plan = RoutePlan(
        id=route_plan_gateway.next_id(),
        shop_id=shop_id,
        delivery_date=delivery_date,
        time_slot_id=time_slot_id,
        order_sequence=all_ids,
    )
    route_plan_gateway.save(route_plan)
    return route_plan


def remove_order_from_route(route_plan: RoutePlan, order_id: OrderId) -> None:
    if order_id not in route_plan.order_sequence:
        logger.warning(
            "Order %s not found in route plan %s sequence",
            order_id,
            route_plan.id,
        )
    route_plan.order_sequence = [
        oid for oid in route_plan.order_sequence if oid != order_id
    ]


def insert_order_into_route(
    route_plan: RoutePlan,
    order: Order,
    shop_coords: CoordinatesDTO | None,
    all_orders: list[Order],
    edge_preferences: PreferenceMap | None = None,
) -> None:
    addr = order.delivery_address

    if addr and addr.coordinates and shop_coords:
        orders_map = {o.id: o for o in all_orders}
        existing_coords = [
            o.delivery_address.coordinates
            for oid in route_plan.order_sequence
            if (o := orders_map.get(OrderId(oid)))
            and o.delivery_address
            and o.delivery_address.coordinates
        ]

        pos = RouteOptimizer.find_best_insertion_position(
            shop_coords=shop_coords,
            existing_sequence_coords=existing_coords,
            new_point_coords=addr.coordinates,
            edge_preferences=edge_preferences,
        )
        sequence = route_plan.order_sequence[:]
        sequence.insert(pos, order.id)
        route_plan.order_sequence = sequence
        logger.info(
            "Inserted order %s at position %d in route plan %s",
            order.id,
            pos,
            route_plan.id,
        )
    else:
        route_plan.order_sequence = [*route_plan.order_sequence, order.id]
        logger.warning(
            "Appended order %s to end of route plan %s"
            " (no coords or no shop_coords)",
            order.id,
            route_plan.id,
        )


def _order_to_point(order: Order, seq: int) -> RoutePointReadModel:
    addr = order.delivery_address
    address_str = f"{addr.street}, {addr.house}" if addr else ""
    if addr and addr.apartment:
        address_str += f", кв. {addr.apartment}"

    coords = None
    if addr and addr.coordinates:
        coords = CoordinatesDTO(
            latitude=addr.coordinates.latitude,
            longitude=addr.coordinates.longitude,
        )

    items_parts = []
    total_price = 0
    for item in order.items:
        items_parts.append(f"{item.name} x{item.quantity}")
        total_price += int(item.price_per_item * item.quantity)

    return RoutePointReadModel(
        order_id=OrderId(order.id),
        sequence=seq,
        client_name=order.client.full_name if order.client else "",
        delivery_phone=order.delivery_phone,
        address=address_str,
        coordinates=coords,
        items_summary=", ".join(items_parts),
        comment=order.comment,
        payment_method=PaymentMethod(order.payment_method),
        total_price=total_price,
    )
