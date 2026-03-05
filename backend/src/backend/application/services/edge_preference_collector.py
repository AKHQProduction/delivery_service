from backend.application.dto.coordinates import CoordinatesDTO, EdgeInput
from backend.application.vars import OrderId
from backend.infrastructure.persistence.tables.orders import Order
from backend.infrastructure.persistence.tables.route_edge_history import (
    RouteEdgeHistory,
)

PREFERENCE_ALPHA = 0.2
PREFERENCE_WINDOW_DAYS = 90

type PreferenceMap = dict[EdgeInput, float]


def extract_edges(
    orders: list[Order], sequence: list[OrderId]
) -> list[EdgeInput]:
    orders_map = {order.id: order for order in orders}

    coords_sequence: list[CoordinatesDTO] = []
    for oid in sequence:
        order = orders_map.get(oid)
        if not order:
            continue
        addr = order.delivery_address
        if addr and addr.coordinates:
            coords_sequence.append(addr.coordinates)

    return [
        EdgeInput(
            from_coords=coords_sequence[i],
            to_coords=coords_sequence[i + 1],
        )
        for i in range(len(coords_sequence) - 1)
    ]


def build_preference_map(
    edges: list[RouteEdgeHistory],
) -> PreferenceMap:
    if not edges:
        return {}

    max_seen = max(e.times_seen for e in edges)
    if max_seen == 0:
        return {}

    return {
        EdgeInput(
            from_coords=CoordinatesDTO(
                latitude=e.from_coords[0],
                longitude=e.from_coords[1],
            ),
            to_coords=CoordinatesDTO(
                latitude=e.to_coords[0],
                longitude=e.to_coords[1],
            ),
        ): e.times_seen / max_seen
        for e in edges
    }
