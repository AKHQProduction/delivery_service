import logging
from datetime import UTC, datetime, timedelta

import httpx
from redis.asyncio import Redis

from backend.application.dto.coordinates import (
    CoordinatesDTO,
    ReverseGeocodeResult,
)
from backend.application.services.geocoder import GeocodingProvider
from backend.bootstrap.config import HereGeocoderConfig

logger = logging.getLogger(__name__)

MONTHLY_COUNTER_KEY = "here_geocoder:monthly:{year}:{month}"
FREE_MONTHLY_LIMIT = 29_990


class HereGeocoderClient(GeocodingProvider):
    def __init__(
        self,
        http_client: httpx.AsyncClient,
        config: HereGeocoderConfig,
        redis: Redis,
    ) -> None:
        self._http = http_client
        self._config = config
        self._redis = redis

    async def geocode(
        self,
        street: str,
        house: str,
        city: str,
        *,
        require_house: bool = True,
    ) -> CoordinatesDTO | None:
        if not self._config.api_key:
            return None

        if not await self._within_limit():
            return None

        query = f"{street} {house}, {city}, Україна"
        try:
            response = await self._http.get(
                "https://geocode.search.hereapi.com/v1/geocode",
                params={
                    "q": query,
                    "apiKey": self._config.api_key,
                    "lang": "uk",
                    "in": "countryCode:UKR",
                },
            )
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPStatusError as exc:
            logger.warning(
                "HERE Geocoding HTTP error: status=%d, query=%s",
                exc.response.status_code,
                query,
            )
            return None
        except Exception as exc:
            logger.exception(
                "HERE Geocoding request failed [%s], query=%s",
                exc.__class__.__name__,
                query,
            )
            return None

        items = data.get("items")
        if not items:
            return None

        try:
            first = items[0]
            result_type = first.get("resultType", "")
            address = first.get("address", {})

            if result_type not in {"houseNumber", "street"}:
                logger.info(
                    "HERE result too vague: resultType=%s, query=%s",
                    result_type,
                    query,
                )
                return None

            if (
                require_house
                and house.strip()
                and not address.get("houseNumber")
            ):
                logger.info(
                    "HERE did not resolve house number, query=%s",
                    query,
                )
                return None

            position = first["position"]
            result = CoordinatesDTO(
                latitude=float(position["lat"]),
                longitude=float(position["lng"]),
            )
        except (KeyError, ValueError, TypeError, IndexError):
            logger.exception(
                "Failed to parse HERE Geocoding response: %s", data
            )
            return None

        await self._increment_counter()
        return result

    async def reverse(
        self, coordinates: CoordinatesDTO
    ) -> ReverseGeocodeResult | None:
        if not self._config.api_key:
            return None

        if not await self._within_limit():
            return None

        try:
            response = await self._http.get(
                "https://revgeocode.search.hereapi.com/v1/revgeocode",
                params={
                    "at": f"{coordinates.latitude},{coordinates.longitude}",
                    "apiKey": self._config.api_key,
                    "lang": "uk",
                },
            )
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPStatusError as exc:
            logger.warning(
                "HERE reverse geocoding HTTP error: status=%d, at=%s,%s",
                exc.response.status_code,
                coordinates.latitude,
                coordinates.longitude,
            )
            return None
        except Exception as exc:
            logger.exception(
                "HERE reverse geocoding request failed [%s], at=%s,%s",
                exc.__class__.__name__,
                coordinates.latitude,
                coordinates.longitude,
            )
            return None

        items = data.get("items")
        if not items:
            return None

        try:
            first = items[0]
            address = first.get("address", {})
            result = ReverseGeocodeResult(
                display_name=address.get("label", first.get("title", "")),
                street=address.get("street"),
                house=address.get("houseNumber"),
                city=address.get("city"),
                district=address.get("district"),
            )
        except (KeyError, TypeError, IndexError):
            logger.exception("Failed to parse HERE reverse response: %s", data)
            return None

        await self._increment_counter()
        return result

    async def _within_limit(self) -> bool:
        now = datetime.now(UTC)
        key = MONTHLY_COUNTER_KEY.format(year=now.year, month=now.month)
        try:
            count = await self._redis.get(key)
            if count is not None and int(count) >= FREE_MONTHLY_LIMIT:
                logger.warning(
                    "HERE Geocoding monthly limit reached: %s", count
                )
                return False
        except Exception as exc:
            logger.exception(
                "Redis counter read failed [%s]", exc.__class__.__name__
            )
        return True

    async def _increment_counter(self) -> None:
        now = datetime.now(UTC)
        key = MONTHLY_COUNTER_KEY.format(year=now.year, month=now.month)
        try:
            ttl = await self._redis.ttl(key)
            pipe = self._redis.pipeline()
            pipe.incr(key)
            if ttl < 0:
                next_month = (now.replace(day=1) + timedelta(days=32)).replace(
                    day=1, hour=0, minute=0, second=0, microsecond=0
                )
                expire_seconds = int((next_month - now).total_seconds())
                pipe.expire(key, expire_seconds)
            await pipe.execute()
        except Exception as exc:
            logger.exception(
                "Redis counter increment failed [%s]",
                exc.__class__.__name__,
            )
