from backend.application.dto.coordinates import CoordinatesDTO
from backend.infrastructure.nominatim import NominatimClient


class Geocoder:
    def __init__(self, nominatim_client: NominatimClient) -> None:
        self._nominatim = nominatim_client

    async def geocode(
        self, street: str, house: str, city: str
    ) -> CoordinatesDTO | None:
        return await self._nominatim.geocode(street, house, city)

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
        return await self._nominatim.geocode(street, house, shop_city)
