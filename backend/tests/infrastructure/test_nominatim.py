from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.application.dto.coordinates import (
    AddressSuggestionDTO,
    CoordinatesDTO,
    ReverseGeocodeResult,
)
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


class TestSuggest:
    @pytest.mark.asyncio()
    async def test_prioritizes_house_number_and_normalizes(
        self, client, http_client
    ):
        response = MagicMock()
        response.json.return_value = [
            {
                "display_name": "Хрещатик, Київ, Україна",
                "lat": "50.4500",
                "lon": "30.5200",
                "address": {"road": "Хрещатик", "city": "Київ"},
            },
            {
                "display_name": "Хрещатик 1, Київ, Україна",
                "lat": "50.4501",
                "lon": "30.5234",
                "address": {
                    "road": "Хрещатик",
                    "house_number": "1",
                    "city": "Київ",
                },
            },
        ]
        http_client.get.return_value = response

        result = await client.suggest("Хрещатик", "Київ", limit=1)

        assert result == [
            AddressSuggestionDTO(
                label="Хрещатик, 1, Київ",
                street="Хрещатик",
                house="1",
                city="Київ",
                coordinates=CoordinatesDTO(
                    latitude=50.4501, longitude=30.5234
                ),
            )
        ]
        http_client.get.assert_awaited_once()
        assert http_client.get.await_args.kwargs["params"]["limit"] == "10"

    @pytest.mark.asyncio()
    async def test_rejects_suggestions_without_city_metadata(
        self, client, http_client
    ):
        response = MagicMock()
        response.json.return_value = [
            {
                "display_name": "Хрещатик, Україна",
                "lat": "50.4501",
                "lon": "30.5234",
                "address": {"road": "Хрещатик"},
            }
        ]
        http_client.get.return_value = response

        result = await client.suggest("Хрещатик", "Київ")

        assert result == []

    @pytest.mark.asyncio()
    async def test_non_positive_limit_skips_request(self, client, http_client):
        result = await client.suggest("Хрещатик", "Київ", limit=0)

        assert result == []
        http_client.get.assert_not_called()

    @pytest.mark.asyncio()
    async def test_includes_quarter_in_compact_label(
        self, client, http_client
    ):
        response = MagicMock()
        response.json.return_value = [
            {
                "lat": "49.4304",
                "lon": "32.0682",
                "address": {
                    "road": "Надпільна вулиця",
                    "house_number": "252",
                    "quarter": "Мікрорайон Соборний",
                    "city": "Черкаси",
                },
            }
        ]
        http_client.get.return_value = response

        result = await client.suggest("Надпільна 252", "Черкаси")

        assert result == [
            AddressSuggestionDTO(
                label="Надпільна вулиця, 252, Мікрорайон Соборний, Черкаси",
                street="Надпільна вулиця",
                house="252",
                city="Черкаси",
                district="Мікрорайон Соборний",
                coordinates=CoordinatesDTO(
                    latitude=49.4304, longitude=32.0682
                ),
            )
        ]


class TestReverse:
    @pytest.mark.asyncio()
    async def test_maps_quarter_to_district(self, client, http_client):
        response = MagicMock()
        response.json.return_value = {
            "display_name": "Надпільна 252, Черкаси",
            "address": {
                "road": "Надпільна вулиця",
                "house_number": "252",
                "quarter": "Мікрорайон Соборний",
                "city": "Черкаси",
            },
        }
        http_client.get.return_value = response

        result = await client.reverse(
            CoordinatesDTO(latitude=49.4304, longitude=32.0682)
        )

        assert result == ReverseGeocodeResult(
            display_name="Надпільна 252, Черкаси",
            street="Надпільна вулиця",
            house="252",
            city="Черкаси",
            district="Мікрорайон Соборний",
        )
