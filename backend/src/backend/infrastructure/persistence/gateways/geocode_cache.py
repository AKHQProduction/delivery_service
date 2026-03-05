import json
import logging

from redis.asyncio import Redis

from backend.application.dto.coordinates import (
    CoordinatesDTO,
    ReverseGeocodeResult,
)
from backend.application.validators import normalize_house, normalize_street
from backend.application.vars import Empty

logger = logging.getLogger(__name__)

GEOCODE_TTL_SECONDS = 86400


class RedisGeocodeCache:
    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    async def get(
        self, city: str, street: str, house: str
    ) -> CoordinatesDTO | Empty | None:
        key = self._build_forward_key(city, street, house)

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
            if parsed.get("not_found"):
                return Empty.EMPTY
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
        key = self._build_forward_key(city, street, house)
        value = json.dumps({"lat": coords.latitude, "lon": coords.longitude})

        try:
            await self._redis.set(
                name=key, value=value, ex=GEOCODE_TTL_SECONDS
            )
        except Exception as exc:
            logger.exception(
                "Redis geocode cache write failed [%s]", exc.__class__.__name__
            )

    async def set_not_found(self, city: str, street: str, house: str) -> None:
        key = self._build_forward_key(city, street, house)
        value = json.dumps({"not_found": True})

        try:
            await self._redis.set(
                name=key, value=value, ex=GEOCODE_TTL_SECONDS
            )
        except Exception as exc:
            logger.exception(
                "Redis geocode cache write failed [%s]", exc.__class__.__name__
            )

    async def get_reverse(
        self, coordinates: CoordinatesDTO
    ) -> ReverseGeocodeResult | None:
        key = self._build_reverse_key(coordinates)

        try:
            data = await self._redis.get(key)
        except Exception as exc:
            logger.exception(
                "Redis reverse cache read failed [%s]",
                exc.__class__.__name__,
            )
            return None

        if data is None:
            return None

        try:
            parsed = json.loads(data)
            return ReverseGeocodeResult(
                display_name=parsed["display_name"],
                street=parsed.get("street"),
                house=parsed.get("house"),
                city=parsed.get("city"),
                district=parsed.get("district"),
            )
        except (KeyError, ValueError, TypeError):
            logger.exception("Failed to parse reverse cache entry: %s", data)
            return None

    async def set_reverse(
        self,
        coordinates: CoordinatesDTO,
        result: ReverseGeocodeResult,
    ) -> None:
        key = self._build_reverse_key(coordinates)
        value = json.dumps({
            "display_name": result.display_name,
            "street": result.street,
            "house": result.house,
            "city": result.city,
            "district": result.district,
        })

        try:
            await self._redis.set(
                name=key, value=value, ex=GEOCODE_TTL_SECONDS
            )
        except Exception as exc:
            logger.exception(
                "Redis reverse cache write failed [%s]",
                exc.__class__.__name__,
            )

    @staticmethod
    def _build_forward_key(city: str, street: str, house: str) -> str:
        c = city.strip().lower()
        s = normalize_street(street)
        h = normalize_house(house)
        return f"geocode:{c}:{s}:{h}"

    @staticmethod
    def _build_reverse_key(coordinates: CoordinatesDTO) -> str:
        lat = f"{coordinates.latitude:.4f}"
        lon = f"{coordinates.longitude:.4f}"
        return f"reverse_geocode:{lat}:{lon}"
