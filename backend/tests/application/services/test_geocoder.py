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
def redis_cache():
    return AsyncMock()


@pytest.fixture()
def client_gateway():
    return AsyncMock()


@pytest.fixture()
def geocoder(nominatim, redis_cache, client_gateway):
    return Geocoder(
        nominatim_client=nominatim,
        redis_cache=redis_cache,
        client_gateway=client_gateway,
    )


class TestGeocode:
    @pytest.mark.asyncio()
    async def test_returns_from_redis_cache(
        self, geocoder, redis_cache, client_gateway, nominatim, coords
    ):
        redis_cache.get.return_value = coords

        result = await geocoder.geocode("Хрещатик", "1", "Київ")

        assert result == coords
        redis_cache.get.assert_awaited_once_with("Київ", "Хрещатик", "1")
        client_gateway.find_coordinates_by_address.assert_not_awaited()
        nominatim.geocode.assert_not_awaited()

    @pytest.mark.asyncio()
    async def test_falls_back_to_db_on_redis_miss(
        self, geocoder, redis_cache, client_gateway, nominatim, coords
    ):
        redis_cache.get.return_value = None
        client_gateway.find_coordinates_by_address.return_value = coords

        result = await geocoder.geocode("Хрещатик", "1", "Київ")

        assert result == coords
        client_gateway.find_coordinates_by_address.assert_awaited_once_with(
            "Хрещатик", "1", "Київ"
        )
        redis_cache.set.assert_awaited_once_with(
            "Київ", "Хрещатик", "1", coords
        )
        nominatim.geocode.assert_not_awaited()

    @pytest.mark.asyncio()
    async def test_falls_back_to_nominatim_on_db_miss(
        self, geocoder, redis_cache, client_gateway, nominatim, coords
    ):
        redis_cache.get.return_value = None
        client_gateway.find_coordinates_by_address.return_value = None
        nominatim.geocode.return_value = coords

        result = await geocoder.geocode("Хрещатик", "1", "Київ")

        assert result == coords
        nominatim.geocode.assert_awaited_once_with("Хрещатик", "1", "Київ")
        redis_cache.set.assert_awaited_once_with(
            "Київ", "Хрещатик", "1", coords
        )

    @pytest.mark.asyncio()
    async def test_returns_none_when_all_miss(
        self, geocoder, redis_cache, client_gateway, nominatim
    ):
        redis_cache.get.return_value = None
        client_gateway.find_coordinates_by_address.return_value = None
        nominatim.geocode.return_value = None

        result = await geocoder.geocode("Невідома", "999", "Місто")

        assert result is None
        redis_cache.set.assert_not_awaited()


class TestGeocodeIfMissing:
    @pytest.mark.asyncio()
    async def test_returns_existing_coordinates(
        self, geocoder, redis_cache, coords
    ):
        result = await geocoder.geocode_if_missing(
            street="Хрещатик",
            house="1",
            coordinates=coords,
            shop_city="Київ",
        )

        assert result == coords
        redis_cache.get.assert_not_awaited()

    @pytest.mark.asyncio()
    async def test_returns_none_when_no_city(self, geocoder, redis_cache):
        result = await geocoder.geocode_if_missing(
            street="Хрещатик",
            house="1",
            coordinates=None,
            shop_city=None,
        )

        assert result is None
        redis_cache.get.assert_not_awaited()

    @pytest.mark.asyncio()
    async def test_delegates_to_geocode(
        self, geocoder, redis_cache, client_gateway, nominatim, coords
    ):
        redis_cache.get.return_value = None
        client_gateway.find_coordinates_by_address.return_value = None
        nominatim.geocode.return_value = coords

        result = await geocoder.geocode_if_missing(
            street="Хрещатик",
            house="1",
            coordinates=None,
            shop_city="Київ",
        )

        assert result == coords
        nominatim.geocode.assert_awaited_once_with("Хрещатик", "1", "Київ")
