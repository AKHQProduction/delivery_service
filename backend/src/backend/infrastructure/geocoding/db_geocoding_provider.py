from backend.application.dto.coordinates import (
    CoordinatesDTO,
    ReverseGeocodeResult,
)
from backend.application.services.geocoder import GeocodingProvider
from backend.infrastructure.persistence.gateways.client_gateway import (
    SQLAlchemyClientGateway,
)


class DBGeocodingProvider(GeocodingProvider):
    def __init__(self, client_gateway: SQLAlchemyClientGateway) -> None:
        self._gateway = client_gateway

    async def geocode(
        self, street: str, house: str, city: str
    ) -> CoordinatesDTO | None:
        return await self._gateway.find_coordinates_by_address(
            street, house, city
        )

    async def reverse(
        self, coordinates: CoordinatesDTO
    ) -> ReverseGeocodeResult | None:
        return await self._gateway.find_address_by_coordinates(coordinates)
