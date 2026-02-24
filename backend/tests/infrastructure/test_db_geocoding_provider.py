from unittest.mock import AsyncMock

import pytest

from backend.application.dto.coordinates import CoordinatesDTO
from backend.infrastructure.geocoding.db_geocoding_provider import (
    DBGeocodingProvider,
)


@pytest.fixture()
def coords():
    return CoordinatesDTO(latitude=50.4501, longitude=30.5234)


@pytest.fixture()
def gateway():
    return AsyncMock()


@pytest.fixture()
def provider(gateway):
    return DBGeocodingProvider(client_gateway=gateway)


class TestGeocode:
    @pytest.mark.asyncio()
    async def test_delegates_to_gateway(self, provider, gateway, coords):
        gateway.find_coordinates_by_address.return_value = coords

        result = await provider.geocode("Хрещатик", "1", "Київ")

        assert result == coords
        gateway.find_coordinates_by_address.assert_awaited_once_with(
            "Хрещатик", "1", "Київ"
        )

    @pytest.mark.asyncio()
    async def test_returns_none(self, provider, gateway):
        gateway.find_coordinates_by_address.return_value = None

        result = await provider.geocode("Невідома", "999", "Місто")

        assert result is None
