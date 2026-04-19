import logging
from abc import abstractmethod
from typing import Protocol

from backend.application.dto.coordinates import (
    AddressSuggestionDTO,
    CoordinatesDTO,
    ReverseGeocodeResult,
)
from backend.application.vars import Empty
from backend.infrastructure.persistence.gateways.geocode_cache import (
    RedisGeocodeCache,
)

logger = logging.getLogger(__name__)


class GeocodingProvider(Protocol):
    @abstractmethod
    async def geocode(
        self,
        street: str,
        house: str,
        city: str,
        *,
        require_house: bool = True,
    ) -> CoordinatesDTO | None: ...

    async def reverse(
        self, coordinates: CoordinatesDTO
    ) -> ReverseGeocodeResult | None:
        return None

    async def suggest(
        self,
        query: str,
        city: str,
        *,
        limit: int = 5,
    ) -> list[AddressSuggestionDTO]:
        return []


class Geocoder:
    def __init__(
        self,
        cache: RedisGeocodeCache,
        providers: list[GeocodingProvider],
    ) -> None:
        self._cache = cache
        self._providers = providers

    async def geocode(
        self,
        street: str,
        house: str,
        city: str,
        *,
        require_house: bool = True,
    ) -> CoordinatesDTO | None:
        cached = await self._cache.get(city, street, house)
        if cached is Empty.EMPTY:
            if require_house:
                logger.info(
                    "Geocode negative cache hit: %s %s, %s",
                    street,
                    house,
                    city,
                )
                return None
        elif cached is not None:
            logger.info(
                "Geocoded from cache: %s %s, %s -> (%s, %s)",
                street,
                house,
                city,
                cached.latitude,
                cached.longitude,
            )
            return cached

        for provider in self._providers:
            result = await provider.geocode(
                street, house, city, require_house=require_house
            )
            if result is not None:
                await self._cache.set(city, street, house, result)
                logger.info(
                    "Geocoded via %s: %s %s, %s -> (%s, %s)",
                    type(provider).__name__,
                    street,
                    house,
                    city,
                    result.latitude,
                    result.longitude,
                )
                return result

        if require_house:
            await self._cache.set_not_found(city, street, house)
        logger.warning(
            "All geocoding providers failed: %s %s, %s",
            street,
            house,
            city,
        )
        return None

    async def geocode_if_missing(
        self,
        *,
        street: str,
        house: str,
        coordinates: CoordinatesDTO | None,
        shop_city: str | None,
        require_house: bool = True,
    ) -> CoordinatesDTO | None:
        if coordinates is not None:
            return coordinates
        if shop_city is None:
            return None
        return await self.geocode(
            street, house, shop_city, require_house=require_house
        )

    async def reverse(
        self, coordinates: CoordinatesDTO
    ) -> ReverseGeocodeResult | None:
        cached = await self._cache.get_reverse(coordinates)
        if cached is not None:
            logger.info(
                "Reverse geocoded from cache: (%s, %s) -> %s | district=%s",
                coordinates.latitude,
                coordinates.longitude,
                cached.display_name,
                cached.district,
            )
            return cached

        partial: ReverseGeocodeResult | None = None
        partial_provider: str = ""

        for provider in self._providers:
            result = await provider.reverse(coordinates)
            if result is None or not result.street:
                continue
            if result.house:
                await self._cache.set_reverse(coordinates, result)
                logger.info(
                    "Reverse geocoded via %s: (%s, %s) -> %s | district=%s",
                    type(provider).__name__,
                    coordinates.latitude,
                    coordinates.longitude,
                    result.display_name,
                    result.district,
                )
                return result
            if partial is None:
                partial = result
                partial_provider = type(provider).__name__

        if partial is not None:
            await self._cache.set_reverse(coordinates, partial)
            logger.info(
                "Reverse geocoded via %s (no house): (%s, %s) -> %s"
                " | district=%s",
                partial_provider,
                coordinates.latitude,
                coordinates.longitude,
                partial.display_name,
                partial.district,
            )
            return partial

        logger.warning(
            "All reverse geocoding providers failed: %s, %s",
            coordinates.latitude,
            coordinates.longitude,
        )
        return None

    async def suggest(
        self,
        query: str,
        city: str,
        *,
        limit: int = 5,
    ) -> list[AddressSuggestionDTO]:
        if limit <= 0:
            return []

        for provider in self._providers:
            result = await provider.suggest(query, city, limit=limit)
            if result:
                return self._dedupe_suggestions(result, limit=limit)
        return []

    @staticmethod
    def _dedupe_suggestions(
        suggestions: list[AddressSuggestionDTO],
        *,
        limit: int,
    ) -> list[AddressSuggestionDTO]:
        deduped: list[AddressSuggestionDTO] = []
        seen: set[tuple[str, str, str, str]] = set()

        for item in suggestions:
            key = (
                item.street.strip().casefold(),
                item.house.strip().casefold(),
                (item.district or "").strip().casefold(),
                item.city.strip().casefold(),
            )
            if key in seen:
                continue

            seen.add(key)
            deduped.append(item)
            if len(deduped) >= limit:
                break

        return deduped
