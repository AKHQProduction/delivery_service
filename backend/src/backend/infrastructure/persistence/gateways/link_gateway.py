import json
from datetime import UTC, datetime, timedelta

from redis.asyncio import Redis

from backend.application.usecases.invite_employee.interfaces import (
    Link,
    LinkGateway,
)


class RedisLinkGateway(LinkGateway):
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
