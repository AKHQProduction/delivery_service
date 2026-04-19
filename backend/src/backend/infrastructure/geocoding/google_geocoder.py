import logging
from datetime import UTC, datetime, timedelta

import httpx
from redis.asyncio import Redis

from backend.application.dto.coordinates import (
    AddressSuggestionDTO,
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

    async def suggest(
        self,
        query: str,
        city: str,
        *,
        limit: int = 5,
    ) -> list[AddressSuggestionDTO]:
        if not self._config.api_key:
            return []

        if limit <= 0:
            return []

        if not await self._within_limit():
            return []

        address = f"{query}, {city}, Україна"
        should_increment = False
        data: object | None = None
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
            should_increment = True
            data = response.json()
        except httpx.HTTPStatusError as exc:
            logger.warning(
                "Google suggest HTTP error: status=%d, address=%s",
                exc.response.status_code,
                address,
            )
            return []
        except Exception as exc:
            logger.exception(
                "Google suggest request failed [%s], address=%s",
                exc.__class__.__name__,
                address,
            )
            return []
        finally:
            if should_increment:
                await self._increment_counter()

        if not isinstance(data, dict):
            return []

        results = data.get("results")
        if not isinstance(results, list) or not results:
            return []

        suggestions: list[AddressSuggestionDTO] = []
        for item in results:
            if not isinstance(item, dict):
                continue
            suggestion = self._normalize_suggestion(item)
            if suggestion is not None:
                suggestions.append(suggestion)

        if not suggestions:
            return []

        suggestions.sort(key=lambda item: not item.house)
        return suggestions[:limit]

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

    @staticmethod
    def _normalize_text(value: object | None) -> str:
        if not isinstance(value, str):
            return ""
        text = value.strip()
        if not text or text.lower() == "none":
            return ""
        return text

    @classmethod
    def _build_suggestion_label(
        cls,
        *,
        street: str,
        house: str,
        district: str,
        city: str,
    ) -> str:
        street_line = ", ".join(part for part in [street, house] if part)
        return ", ".join(
            part for part in [street_line, district, city] if part
        )

    def _normalize_suggestion(
        self,
        item: dict[str, object],
    ) -> AddressSuggestionDTO | None:
        try:
            components_by_type: dict[str, str] = {}
            address_components = item.get("address_components")
            if not isinstance(address_components, list):
                return None

            for component in address_components:
                if not isinstance(component, dict):
                    continue
                long_name = self._normalize_text(component.get("long_name"))
                if not long_name:
                    continue
                types = component.get("types", [])
                if not isinstance(types, list):
                    continue
                for component_type in types:
                    if isinstance(component_type, str):
                        components_by_type[component_type] = long_name

            street = self._normalize_text(components_by_type.get("route"))
            if not street:
                return None

            geometry = item.get("geometry", {})
            if not isinstance(geometry, dict):
                return None
            location = geometry.get("location", {})
            if not isinstance(location, dict):
                return None
            coordinates = None
            lat = location.get("lat")
            lng = location.get("lng")
            if lat is not None and lng is not None:
                coordinates = CoordinatesDTO(
                    latitude=float(lat),
                    longitude=float(lng),
                )
            else:
                return None

            city = self._normalize_text(
                components_by_type.get("locality")
            ) or self._normalize_text(components_by_type.get("postal_town"))
            if not city:
                return None

            district = (
                self._normalize_text(components_by_type.get("sublocality"))
                or self._normalize_text(
                    components_by_type.get("sublocality_level_1")
                )
                or self._normalize_text(components_by_type.get("neighborhood"))
            )

            house = self._normalize_text(
                components_by_type.get("street_number")
            )
            label = self._build_suggestion_label(
                street=street,
                house=house,
                district=district,
                city=city,
            )

            return AddressSuggestionDTO(
                label=label,
                street=street,
                house=house,
                city=city,
                coordinates=coordinates,
                district=district or None,
            )
        except Exception as exc:
            logger.exception(
                "Failed to parse Google suggest item [%s]: %s",
                exc.__class__.__name__,
                item,
            )
            return None
