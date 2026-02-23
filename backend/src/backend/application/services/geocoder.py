import logging
from abc import abstractmethod
from typing import Protocol

from backend.application.dto.coordinates import (
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
        self, street: str, house: str, city: str
    ) -> CoordinatesDTO | None: ...

    async def reverse(
        self, coordinates: CoordinatesDTO
    ) -> ReverseGeocodeResult | None:
        return None


class Geocoder:
    def __init__(
        self,
        cache: RedisGeocodeCache,
        providers: list[GeocodingProvider],
    ) -> None:
        self._cache = cache
        self._providers = providers

    async def geocode(
        self, street: str, house: str, city: str
    ) -> CoordinatesDTO | None:
        cached = await self._cache.get(city, street, house)
        if cached is Empty.EMPTY:
            logger.info(
                "Geocode negative cache hit: %s %s, %s",
                street,
                house,
                city,
            )
            return None
        if cached is not None:
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
            result = await provider.geocode(street, house, city)
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
    ) -> CoordinatesDTO | None:
        if coordinates is not None:
            return coordinates
        if shop_city is None:
            return None
        return await self.geocode(street, house, shop_city)

    async def reverse(
        self, coordinates: CoordinatesDTO
    ) -> ReverseGeocodeResult | None:
        cached = await self._cache.get_reverse(coordinates)
        if cached is not None:
            logger.info(
                "Reverse geocoded from cache: (%s, %s) -> %s",
                coordinates.latitude,
                coordinates.longitude,
                cached.display_name,
            )
            return cached

        for provider in self._providers:
            result = await provider.reverse(coordinates)
            if result is not None:
                await self._cache.set_reverse(coordinates, result)
                logger.info(
                    "Reverse geocoded via %s: (%s, %s) -> %s",
                    type(provider).__name__,
                    coordinates.latitude,
                    coordinates.longitude,
                    result.display_name,
                )
                return result

        logger.warning(
            "All reverse geocoding providers failed: %s, %s",
            coordinates.latitude,
            coordinates.longitude,
        )
        return None
