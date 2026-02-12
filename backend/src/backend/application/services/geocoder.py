import logging

from backend.application.dto.coordinates import CoordinatesDTO
from backend.infrastructure.nominatim import NominatimClient
from backend.infrastructure.persistence.gateways import (
    RedisGeocodeCache,
    SQLAlchemyClientGateway,
)

logger = logging.getLogger(__name__)


class Geocoder:
    def __init__(
        self,
        nominatim_client: NominatimClient,
        redis_cache: RedisGeocodeCache,
        client_gateway: SQLAlchemyClientGateway,
    ) -> None:
        self._nominatim = nominatim_client
        self._redis_cache = redis_cache
        self._client_gateway = client_gateway

    async def geocode(
        self, street: str, house: str, city: str
    ) -> CoordinatesDTO | None:
        cached = await self._redis_cache.get(city, street, house)
        if cached is not None:
            return cached

        from_db = await self._client_gateway.find_coordinates_by_address(
            street, house, city
        )
        if from_db is not None:
            await self._redis_cache.set(city, street, house, from_db)
            return from_db

        from_api = await self._nominatim.geocode(street, house, city)
        if from_api is not None:
            await self._redis_cache.set(city, street, house, from_api)
            return from_api

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
