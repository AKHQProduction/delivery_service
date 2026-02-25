from dataclasses import dataclass

from backend.application.dto.coordinates import CoordinatesDTO
from backend.application.vars import (
    OrderId,
    PaymentMethod,
    RoutePlanId,
)


@dataclass(frozen=True)
class RoutePointReadModel:
    order_id: OrderId
    sequence: int
    client_name: str
    delivery_phone: str
    address: str
    coordinates: CoordinatesDTO | None
    items_summary: str
    comment: str | None
    payment_method: PaymentMethod
    total_price: int


@dataclass(frozen=True)
class RouteStatsReadModel:
    total_orders: int
    unique_addresses: int
    total_distance_meters: int
    total_duration_seconds: int


@dataclass(frozen=True)
class RouteGeometryReadModel:
    encoded_polyline: str
    distance_meters: int
    duration_seconds: int


@dataclass(frozen=True)
class RouteReadModel:
    route_plan_id: RoutePlanId
    delivery_date: str
    time_slot: str | None
    points: list[RoutePointReadModel]
    unroutable_orders: list[RoutePointReadModel]
    stats: RouteStatsReadModel
    geometry: RouteGeometryReadModel | None = None
