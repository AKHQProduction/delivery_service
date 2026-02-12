from backend.application.dto.coordinates import CoordinatesDTO
from backend.infrastructure.nominatim import NominatimClient
from backend.infrastructure.persistence.gateways import RedisGeocodeCache


class Geocoder:
    def __init__(
        self,
        nominatim_client: NominatimClient,
        redis_cache: RedisGeocodeCache,
    ) -> None:
        self._nominatim = nominatim_client
        self._redis_cache = redis_cache

    async def geocode(
        self, street: str, house: str, city: str
    ) -> CoordinatesDTO | None:
        cached = await self._redis_cache.get(city, street, house)
        if cached is not None:
            return cached

        result = await self._nominatim.geocode(street, house, city)
        if result is not None:
            await self._redis_cache.set(city, street, house, result)

        return result

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
