import logging
from datetime import UTC, datetime, timedelta

import httpx
from redis.asyncio import Redis

from backend.application.dto.coordinates import (
    CoordinatesDTO,
    ReverseGeocodeResult,
)
from backend.application.services.geocoder import GeocodingProvider
from backend.bootstrap.config import GoogleGeocoderConfig

logger = logging.getLogger(__name__)

MONTHLY_COUNTER_KEY = "google_geocoder:monthly:{year}:{month}"
FREE_MONTHLY_LIMIT = 9990


class GoogleGeocoderClient(GeocodingProvider):
    def __init__(
        self,
        http_client: httpx.AsyncClient,
        config: GoogleGeocoderConfig,
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

        address = f"{street} {house}, {city}, Україна"
        try:
            response = await self._http.get(
                "https://maps.googleapis.com/maps/api/geocode/json",
                params={
                    "address": address,
                    "key": self._config.api_key,
                    "language": "uk",
                    "components": "country:UA",
                },
            )
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPStatusError as exc:
            logger.warning(
                "Google Geocoding HTTP error: status=%d, address=%s",
                exc.response.status_code,
                address,
            )
            return None
        except Exception as exc:
            logger.exception(
                "Google Geocoding request failed [%s], address=%s",
                exc.__class__.__name__,
                address,
            )
            return None

        results = data.get("results")
        if not results:
            return None

        try:
            first = results[0]
            location_type = first.get("geometry", {}).get("location_type", "")

            if location_type == "APPROXIMATE":
                logger.info(
                    "Google result too vague: location_type=%s, address=%s",
                    location_type,
                    address,
                )
                return None

            if require_house and house.strip():
                component_types = {
                    t
                    for c in first.get("address_components", [])
                    for t in c.get("types", [])
                }
                if "street_number" not in component_types:
                    logger.info(
                        "Google did not resolve house number, address=%s",
                        address,
                    )
                    return None

            location = first["geometry"]["location"]
            result = CoordinatesDTO(
                latitude=float(location["lat"]),
                longitude=float(location["lng"]),
            )
        except (KeyError, ValueError, TypeError, IndexError):
            logger.exception(
                "Failed to parse Google Geocoding response: %s", data
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
                "https://maps.googleapis.com/maps/api/geocode/json",
                params={
                    "latlng": f"{coordinates.latitude},"
                    f"{coordinates.longitude}",
                    "key": self._config.api_key,
                    "language": "uk",
                    "result_type": "street_address|route",
                },
            )
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPStatusError as exc:
            logger.warning(
                "Google reverse geocoding HTTP error: status=%d, at=%s,%s",
                exc.response.status_code,
                coordinates.latitude,
                coordinates.longitude,
            )
            return None
        except Exception as exc:
            logger.exception(
                "Google reverse geocoding request failed [%s], at=%s,%s",
                exc.__class__.__name__,
                coordinates.latitude,
                coordinates.longitude,
            )
            return None

        results = data.get("results")
        if not results:
            return None

        try:
            first = results[0]
            components = {
                c["types"][0]: c["long_name"]
                for c in first.get("address_components", [])
                if c.get("types")
            }
            result = ReverseGeocodeResult(
                display_name=first["formatted_address"],
                street=components.get("route"),
                house=components.get("street_number"),
                city=components.get("locality"),
                district=components.get("sublocality")
                or components.get("sublocality_level_1"),
            )
        except (KeyError, ValueError, TypeError, IndexError):
            logger.exception(
                "Failed to parse Google reverse response: %s", data
            )
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
                    "Google Geocoding monthly limit reached: %s", count
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
