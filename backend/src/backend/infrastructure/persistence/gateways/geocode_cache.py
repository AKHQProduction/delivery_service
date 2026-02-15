import json
import logging

from redis.asyncio import Redis

from backend.application.dto.coordinates import CoordinatesDTO

logger = logging.getLogger(__name__)

GEOCODE_TTL_SECONDS = 86400


class RedisGeocodeCache:
    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    async def get(
        self, city: str, street: str, house: str
    ) -> CoordinatesDTO | None:
        key = self._build_key(city, street, house)

        try:
            data = await self._redis.get(key)
        except Exception as exc:
            logger.exception(
                "Redis geocode cache read failed [%s]", exc.__class__.__name__
            )
            return None

        if data is None:
            return None

        try:
            parsed = json.loads(data)
            return CoordinatesDTO(
                latitude=parsed["lat"],
                longitude=parsed["lon"],
            )
        except (KeyError, ValueError, TypeError):
            logger.exception("Failed to parse geocode cache entry: %s", data)
            return None

    async def set(
        self,
        city: str,
        street: str,
        house: str,
        coords: CoordinatesDTO,
    ) -> None:
        key = self._build_key(city, street, house)
        value = json.dumps({"lat": coords.latitude, "lon": coords.longitude})

        try:
            await self._redis.set(
                name=key, value=value, ex=GEOCODE_TTL_SECONDS
            )
        except Exception as exc:
            logger.exception(
                "Redis geocode cache write failed [%s]", exc.__class__.__name__
            )

    @staticmethod
    def _build_key(city: str, street: str, house: str) -> str:
        c = city.strip().lower()
        s = street.strip().lower()
        h = house.strip().lower()
        return f"geocode:{c}:{s}:{h}"
