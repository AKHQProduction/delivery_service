from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.application.dto.coordinates import CoordinatesDTO
from backend.infrastructure.nominatim import NominatimClient


@pytest.fixture()
def coords():
    return CoordinatesDTO(latitude=50.4501, longitude=30.5234)


@pytest.fixture()
def cache():
    return AsyncMock()


@pytest.fixture()
def http_client():
    return AsyncMock()


@pytest.fixture()
def config():
    cfg = AsyncMock()
    cfg.url = "http://nominatim.local"
    return cfg


@pytest.fixture()
def client(http_client, config, cache):
    return NominatimClient(http_client=http_client, config=config, cache=cache)


class TestCaching:
    @pytest.mark.asyncio()
    async def test_returns_from_cache(
        self, client, cache, http_client, coords
    ):
        cache.get.return_value = coords

        result = await client.geocode("Хрещатик", "1", "Київ")

        assert result == coords
        cache.get.assert_awaited_once_with("Київ", "Хрещатик", "1")
        http_client.get.assert_not_awaited()

    @pytest.mark.asyncio()
    async def test_stores_in_cache_on_api_hit(
        self, client, cache, http_client, coords
    ):
        cache.get.return_value = None
        response = MagicMock()
        response.json.return_value = [{"lat": "50.4501", "lon": "30.5234"}]
        http_client.get.return_value = response

        result = await client.geocode("Хрещатик", "1", "Київ")

        assert result == coords
        cache.set.assert_awaited_once_with("Київ", "Хрещатик", "1", coords)

    @pytest.mark.asyncio()
    async def test_does_not_cache_on_api_miss(
        self, client, cache, http_client
    ):
        cache.get.return_value = None
        response = MagicMock()
        response.json.return_value = []
        http_client.get.return_value = response

        result = await client.geocode("Невідома", "999", "Місто")

        assert result is None
        cache.set.assert_not_awaited()
