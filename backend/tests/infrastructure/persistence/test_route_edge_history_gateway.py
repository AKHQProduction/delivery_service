import uuid
from datetime import datetime, timedelta

import pytest
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.dto.coordinates import CoordinatesDTO, EdgeInput
from backend.application.vars import KYIV_TZ, ShopId
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyRouteEdgeHistoryGateway,
)
from backend.infrastructure.persistence.tables.route_edge_history import (
    RouteEdgeHistory,
)


@pytest.fixture()
def edge_gateway(session: AsyncSession) -> SQLAlchemyRouteEdgeHistoryGateway:
    return SQLAlchemyRouteEdgeHistoryGateway(session)


@pytest.mark.asyncio()
async def test_upsert_new_edges(
    session: AsyncSession,
    create_shop,
    edge_gateway: SQLAlchemyRouteEdgeHistoryGateway,
) -> None:
    shop_id = await create_shop()
    await session.flush()

    edges = [
        EdgeInput(
            from_coords=CoordinatesDTO(50.1, 30.1),
            to_coords=CoordinatesDTO(50.2, 30.2),
        ),
        EdgeInput(
            from_coords=CoordinatesDTO(50.2, 30.2),
            to_coords=CoordinatesDTO(50.3, 30.3),
        ),
    ]

    await edge_gateway.upsert_edges(shop_id, edges)
    await session.flush()

    rows = await edge_gateway.load_preferences(shop_id)
    assert len(rows) == 2
    assert all(r.times_seen == 1 for r in rows)


@pytest.mark.asyncio()
async def test_upsert_increments_frequency(
    session: AsyncSession,
    create_shop,
    edge_gateway: SQLAlchemyRouteEdgeHistoryGateway,
) -> None:
    shop_id = await create_shop()
    await session.flush()

    edge = EdgeInput(
        from_coords=CoordinatesDTO(50.1, 30.1),
        to_coords=CoordinatesDTO(50.2, 30.2),
    )

    await edge_gateway.upsert_edges(shop_id, [edge])
    await session.flush()

    await edge_gateway.upsert_edges(shop_id, [edge])
    await session.flush()

    session.expire_all()
    rows = await edge_gateway.load_preferences(shop_id)
    assert len(rows) == 1
    assert rows[0].times_seen == 2


@pytest.mark.asyncio()
async def test_load_preferences_filters_by_date(
    session: AsyncSession,
    create_shop,
    edge_gateway: SQLAlchemyRouteEdgeHistoryGateway,
) -> None:
    shop_id = await create_shop()
    await session.flush()

    edge = EdgeInput(
        from_coords=CoordinatesDTO(50.1, 30.1),
        to_coords=CoordinatesDTO(50.2, 30.2),
    )

    await edge_gateway.upsert_edges(shop_id, [edge])
    await session.flush()

    old_date = datetime.now(KYIV_TZ).replace(tzinfo=None) - timedelta(days=120)
    await session.execute(
        update(RouteEdgeHistory)
        .where(RouteEdgeHistory.shop_id == shop_id)
        .values(last_seen=old_date)
    )
    await session.flush()

    rows = await edge_gateway.load_preferences(shop_id, since_days=90)
    assert len(rows) == 0


@pytest.mark.asyncio()
async def test_load_preferences_empty_shop(
    edge_gateway: SQLAlchemyRouteEdgeHistoryGateway,
) -> None:
    unknown_shop = ShopId(uuid.uuid4())
    rows = await edge_gateway.load_preferences(unknown_shop)
    assert rows == []


@pytest.mark.asyncio()
async def test_upsert_empty_edges(
    session: AsyncSession,
    create_shop,
    edge_gateway: SQLAlchemyRouteEdgeHistoryGateway,
) -> None:
    shop_id = await create_shop()
    await session.flush()

    await edge_gateway.upsert_edges(shop_id, [])

    rows = await edge_gateway.load_preferences(shop_id)
    assert rows == []


@pytest.mark.asyncio()
async def test_load_preferences_isolated_by_shop(
    session: AsyncSession,
    create_shop,
    edge_gateway: SQLAlchemyRouteEdgeHistoryGateway,
) -> None:
    shop_a = await create_shop(name="Shop A")
    shop_b = await create_shop(name="Shop B")
    await session.flush()

    edge = EdgeInput(
        from_coords=CoordinatesDTO(50.1, 30.1),
        to_coords=CoordinatesDTO(50.2, 30.2),
    )

    await edge_gateway.upsert_edges(shop_a, [edge])
    await session.flush()

    rows_a = await edge_gateway.load_preferences(shop_a)
    rows_b = await edge_gateway.load_preferences(shop_b)

    assert len(rows_a) == 1
    assert len(rows_b) == 0
