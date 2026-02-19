from uuid import UUID, uuid4

from redis.asyncio import Redis

from backend.application.vars import UserId

SESSION_TTL = 604800  # 7 days


class RedisSessionGateway:
    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    async def set_session(self, user_id: UserId) -> str:
        session_id = str(uuid4())
        await self._redis.set(
            name=f"session:{session_id}",
            value=str(user_id),
            ex=SESSION_TTL,
        )
        return session_id

    async def authenticate(self, session_id: str) -> UserId | None:
        if data := await self._redis.get(f"session:{session_id}"):
            return UserId(UUID(data))
        return None

    async def remove_session(self, session_id: str) -> None:
        await self._redis.delete(f"session:{session_id}")
