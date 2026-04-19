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
from backend.bootstrap.config import HereGeocoderConfig

logger = logging.getLogger(__name__)

MONTHLY_COUNTER_KEY = "here_geocoder:monthly:{year}:{month}"
FREE_MONTHLY_LIMIT = 29_990
SUGGEST_RAW_LIMIT = 10


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
            city = self._normalize_text(address.get("city"))
            district = self._normalize_text(address.get("district"))
            if district and city and district.casefold() == city.casefold():
                district = ""

            result = ReverseGeocodeResult(
                display_name=address.get("label", first.get("title", "")),
                street=address.get("street"),
                house=address.get("houseNumber"),
                city=city or None,
                district=district or None,
            )
        except (KeyError, TypeError, IndexError):
            logger.exception("Failed to parse HERE reverse response: %s", data)
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

        search_query = f"{query}, {city}, Україна"
        request_limit = max(limit, SUGGEST_RAW_LIMIT)
        should_increment = False
        data: object | None = None
        try:
            response = await self._http.get(
                "https://geocode.search.hereapi.com/v1/geocode",
                params={
                    "q": search_query,
                    "apiKey": self._config.api_key,
                    "lang": "uk",
                    "in": "countryCode:UKR",
                    "limit": str(request_limit),
                },
            )
            response.raise_for_status()
            should_increment = True
            data = response.json()
        except httpx.HTTPStatusError as exc:
            logger.warning(
                "HERE suggest HTTP error: status=%d, query=%s",
                exc.response.status_code,
                search_query,
            )
            return []
        except Exception as exc:
            logger.exception(
                "HERE suggest request failed [%s], query=%s",
                exc.__class__.__name__,
                search_query,
            )
            return []
        finally:
            if should_increment:
                await self._increment_counter()

        if not isinstance(data, dict):
            return []

        items = data.get("items")
        if not isinstance(items, list) or not items:
            return []

        suggestions: list[AddressSuggestionDTO] = []
        for item in items:
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
            result_type = self._normalize_text(item.get("resultType"))
            if result_type not in {"houseNumber", "street"}:
                return None

            address = item.get("address", {})
            if not isinstance(address, dict):
                return None

            street = self._normalize_text(address.get("street"))
            if not street:
                return None

            position = item.get("position", {})
            if not isinstance(position, dict):
                return None

            coordinates = None
            lat = position.get("lat")
            lng = position.get("lng")
            if lat is not None and lng is not None:
                coordinates = CoordinatesDTO(
                    latitude=float(lat),
                    longitude=float(lng),
                )
            else:
                return None

            city = self._normalize_text(address.get("city"))
            if not city:
                return None

            district = self._normalize_text(
                address.get("district")
            ) or self._normalize_text(address.get("subdistrict"))

            house = self._normalize_text(address.get("houseNumber"))
            label = self._build_suggestion_label(
                street=street,
                house=house,
                district=district,
                city=city,
            )

            return AddressSuggestionDTO(
                label=label,
                street=str(street),
                house=house,
                city=city,
                coordinates=coordinates,
                district=district or None,
            )
        except Exception as exc:
            logger.exception(
                "Failed to parse HERE suggest item [%s]: %s",
                exc.__class__.__name__,
                item,
            )
            return None
