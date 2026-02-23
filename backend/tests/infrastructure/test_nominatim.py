from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.application.dto.coordinates import CoordinatesDTO
from backend.infrastructure.geocoding.nominatim import NominatimClient


@pytest.fixture()
def coords():
    return CoordinatesDTO(latitude=50.4501, longitude=30.5234)


@pytest.fixture()
def http_client():
    return AsyncMock()


@pytest.fixture()
def config():
    cfg = MagicMock()
    cfg.url = "http://nominatim.local"
    return cfg


@pytest.fixture()
def client(http_client, config):
    return NominatimClient(http_client=http_client, config=config)


class TestGeocode:
    @pytest.mark.asyncio()
    async def test_structured_search_success(
        self, client, http_client, coords
    ):
        response = MagicMock()
        response.json.return_value = [
            {
                "lat": "50.4501",
                "lon": "30.5234",
                "address": {"road": "Хрещатик", "house_number": "1"},
            }
        ]
        http_client.get.return_value = response

        result = await client.geocode("Хрещатик", "1", "Київ")

        assert result == coords

    @pytest.mark.asyncio()
    async def test_freetext_fallback(self, client, http_client, coords):
        structured_response = MagicMock()
        structured_response.json.return_value = []

        freetext_response = MagicMock()
        freetext_response.json.return_value = [
            {
                "lat": "50.4501",
                "lon": "30.5234",
                "address": {"road": "Хрещатик", "house_number": "1"},
            }
        ]

        http_client.get.side_effect = [structured_response, freetext_response]

        result = await client.geocode("Хрещатик", "1", "Київ")

        assert result == coords
        assert http_client.get.await_count == 2

    @pytest.mark.asyncio()
    async def test_returns_none_when_all_empty(self, client, http_client):
        response = MagicMock()
        response.json.return_value = []
        http_client.get.return_value = response

        result = await client.geocode("Невідома", "999", "Місто")

        assert result is None

    @pytest.mark.asyncio()
    async def test_no_road_rejected(self, client, http_client):
        response = MagicMock()
        response.json.return_value = [
            {
                "lat": "50.4501",
                "lon": "30.5234",
                "address": {"city": "Київ"},
            }
        ]
        http_client.get.return_value = response

        result = await client.geocode("Хрещатик", "1", "Київ")

        assert result is None

    @pytest.mark.asyncio()
    async def test_missing_house_number_rejected(self, client, http_client):
        response = MagicMock()
        response.json.return_value = [
            {
                "lat": "50.4501",
                "lon": "30.5234",
                "address": {"road": "Хрещатик"},
            }
        ]
        http_client.get.return_value = response

        result = await client.geocode("Хрещатик", "1", "Київ")

        assert result is None
