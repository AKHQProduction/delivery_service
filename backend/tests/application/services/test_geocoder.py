from unittest.mock import AsyncMock

import pytest

from backend.application.dto.coordinates import CoordinatesDTO
from backend.application.services.geocoder import Geocoder


@pytest.fixture()
def coords():
    return CoordinatesDTO(latitude=50.4501, longitude=30.5234)


@pytest.fixture()
def nominatim():
    return AsyncMock()


@pytest.fixture()
def geocoder(nominatim):
    return Geocoder(nominatim_client=nominatim)


class TestGeocode:
    @pytest.mark.asyncio()
    async def test_delegates_to_nominatim(self, geocoder, nominatim, coords):
        nominatim.geocode.return_value = coords

        result = await geocoder.geocode("Хрещатик", "1", "Київ")

        assert result == coords
        nominatim.geocode.assert_awaited_once_with("Хрещатик", "1", "Київ")

    @pytest.mark.asyncio()
    async def test_returns_none_when_nominatim_returns_none(
        self, geocoder, nominatim
    ):
        nominatim.geocode.return_value = None

        result = await geocoder.geocode("Невідома", "999", "Місто")

        assert result is None


class TestGeocodeIfMissing:
    @pytest.mark.asyncio()
    async def test_returns_existing_coordinates(
        self, geocoder, nominatim, coords
    ):
        result = await geocoder.geocode_if_missing(
            street="Хрещатик",
            house="1",
            coordinates=coords,
            shop_city="Київ",
        )

        assert result == coords
        nominatim.geocode.assert_not_awaited()

    @pytest.mark.asyncio()
    async def test_returns_none_when_no_city(self, geocoder, nominatim):
        result = await geocoder.geocode_if_missing(
            street="Хрещатик",
            house="1",
            coordinates=None,
            shop_city=None,
        )

        assert result is None
        nominatim.geocode.assert_not_awaited()

    @pytest.mark.asyncio()
    async def test_delegates_to_geocode(self, geocoder, nominatim, coords):
        nominatim.geocode.return_value = coords

        result = await geocoder.geocode_if_missing(
            street="Хрещатик",
            house="1",
            coordinates=None,
            shop_city="Київ",
        )

        assert result == coords
        nominatim.geocode.assert_awaited_once_with("Хрещатик", "1", "Київ")
