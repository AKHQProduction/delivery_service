import base64
from uuid import uuid4

from redis.asyncio import Redis

FILE_TTL_SECONDS = 300


class RedisFileStorage:
    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    async def save(self, file_bytes: bytes, filename: str) -> str:
        file_id = str(uuid4())
        key = f"file:{file_id}"

        data = {
            "content": base64.b64encode(file_bytes).decode(),
            "filename": filename,
        }

        await self._redis.hset(key, mapping=data)  # type: ignore[misc]
        await self._redis.expire(key, FILE_TTL_SECONDS)  # type: ignore[misc]

        return file_id

    async def get(self, file_id: str) -> tuple[bytes, str] | None:
        key = f"file:{file_id}"
        data = await self._redis.hgetall(key)  # type: ignore[misc]

        if not data:
            return None

        content = base64.b64decode(data["content"])
        filename = data["filename"]

        return content, filename
