import json
from datetime import UTC, datetime, timedelta
from uuid import UUID

from redis.asyncio import Redis

from backend.application.usecases.invite_employee.interfaces import (
    Link,
)
from backend.application.vars import ShopId, ShopRole


class RedisLinkGateway:
    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    async def add(self, link: Link) -> None:
        now = datetime.now(tz=UTC)
        midnight = (now + timedelta(days=1)).replace(
            hour=0, minute=0, second=0
        )
        ttl = int((midnight - now).total_seconds())

        await self._redis.set(
            name=link.payload,
            value=json.dumps({
                "shop_id": str(link.shop_id),
                "role": link.role,
                "payload": link.payload,
                "full_name": link.full_name,
            }),
            ex=ttl,
        )

    async def load_by_payload(self, payload: str) -> Link | None:
        if data := await self._redis.get(payload):
            json_data = json.loads(data)
            return Link(
                payload=payload,
                full_name=json_data["full_name"],
                role=ShopRole(json_data["role"]),
                shop_id=ShopId(UUID(json_data["shop_id"])),
            )
        return None

    async def delete(self, payload: str) -> None:
        await self._redis.delete(payload)
