from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func
from uuid_utils.compat import uuid7

from backend.application.dto.coordinates import EdgeInput
from backend.application.vars import KYIV_TZ, RouteEdgeHistoryId, ShopId
from backend.infrastructure.persistence.tables.route_edge_history import (
    RouteEdgeHistory,
)


class SQLAlchemyRouteEdgeHistoryGateway:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def next_id() -> RouteEdgeHistoryId:
        return RouteEdgeHistoryId(uuid7())

    async def upsert_edges(
        self, shop_id: ShopId, edges: list[EdgeInput]
    ) -> None:
        if not edges:
            return

        unique_edges = list(dict.fromkeys(edges))

        stmt = pg_insert(RouteEdgeHistory).values([
            {
                "id": self.next_id(),
                "shop_id": shop_id,
                "from_coords": [
                    e.from_coords.latitude,
                    e.from_coords.longitude,
                ],
                "to_coords": [
                    e.to_coords.latitude,
                    e.to_coords.longitude,
                ],
            }
            for e in unique_edges
        ])
        stmt = stmt.on_conflict_do_update(
            constraint="uq_route_edge_shop_coords",
            set_={
                "times_seen": RouteEdgeHistory.times_seen + 1,
                "last_seen": func.now(),
                "updated_at": func.now(),
            },
        )
        await self._session.execute(stmt)

    async def load_preferences(
        self, shop_id: ShopId, since_days: int = 90
    ) -> list[RouteEdgeHistory]:
        cutoff = datetime.now(KYIV_TZ).replace(tzinfo=None) - timedelta(
            days=since_days
        )
        query = select(RouteEdgeHistory).where(
            RouteEdgeHistory.shop_id == shop_id,
            RouteEdgeHistory.last_seen >= cutoff,
        )
        result = await self._session.execute(query)
        return list(result.scalars().all())
