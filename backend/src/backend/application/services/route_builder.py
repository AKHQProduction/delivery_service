from datetime import date, time

from backend.application.dto.coordinates import CoordinatesDTO
from backend.application.dto.gateways.route_gateway import (
    RouteGeometryReadModel,
    RoutePointReadModel,
    RouteReadModel,
    RouteStatsReadModel,
)
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


async def resolve_time_slot(
    time_slot_gateway: SQLAlchemyTimeSlotGateway,
    time_slot_id: TimeSlotId | None,
) -> tuple[str | None, time | None, time | None]:
    if not time_slot_id:
        return None, None, None
    ts = await time_slot_gateway.load(time_slot_id)
    if not ts:
        return None, None, None
    label = (
        f"{ts.start_time.strftime('%H:%M')}-{ts.end_time.strftime('%H:%M')}"
    )
    return label, ts.start_time, ts.end_time


def build_route_read_model(
    route_plan_id: RoutePlanId,
    delivery_date: str,
    time_slot: str | None,
    ordered_orders: list[Order],
    unroutable_orders: list[Order],
    geometry: RouteGeometryReadModel | None,
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
        total_distance_meters=geometry.distance_meters if geometry else 0,
        total_duration_seconds=geometry.duration_seconds if geometry else 0,
    )

    return RouteReadModel(
        route_plan_id=route_plan_id,
        delivery_date=delivery_date,
        time_slot=time_slot,
        points=points,
        unroutable_orders=unroutable,
        stats=stats,
        geometry=geometry,
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


def collect_waypoints(
    shop_coords: CoordinatesDTO,
    orders: list[Order],
) -> list[tuple[float, float]]:
    waypoints: list[tuple[float, float]] = [
        (shop_coords.latitude, shop_coords.longitude),
    ]
    for order in orders:
        addr = order.delivery_address
        if addr and addr.coordinates:
            waypoints.append((
                addr.coordinates.latitude,
                addr.coordinates.longitude,
            ))
    return waypoints


def build_coordinates_snapshot(
    orders: list[Order],
    order_sequence: list,
) -> dict:
    orders_map = {str(order.id): order for order in orders}
    snapshot = {}
    for oid in order_sequence:
        order = orders_map.get(str(oid))
        if (
            order
            and order.delivery_address
            and order.delivery_address.coordinates
        ):
            coords = order.delivery_address.coordinates
            snapshot[str(oid)] = [coords.latitude, coords.longitude]
    return snapshot


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
        coordinates_snapshot=build_coordinates_snapshot(orders, all_ids),
    )
    route_plan_gateway.save(route_plan)
    return route_plan


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
