from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from backend.application.dto.coordinates import (
    AddressSuggestionDTO,
    CoordinatesDTO,
)
from backend.infrastructure.geocoding.google_geocoder import (
    FREE_MONTHLY_LIMIT,
    GoogleGeocoderClient,
)


@pytest.fixture()
def config():
    cfg = MagicMock()
    cfg.api_key = "test-key"  # pragma: allowlist secret
    return cfg


@pytest.fixture()
def redis():
    return AsyncMock()


@pytest.fixture()
def http_client():
    return AsyncMock()


@pytest.fixture()
def client(http_client, config, redis):
    return GoogleGeocoderClient(
        http_client=http_client, config=config, redis=redis
    )


class TestGeocode:
    @pytest.mark.asyncio()
    async def test_success(self, client, http_client, redis):
        redis.get.return_value = None
        redis.ttl.return_value = -2
        pipeline_mock = MagicMock()
        pipeline_mock.execute = AsyncMock()
        redis.pipeline = MagicMock(return_value=pipeline_mock)

        response = MagicMock()
        response.json.return_value = {
            "results": [
                {
                    "geometry": {
                        "location": {"lat": "50.45", "lng": "30.52"},
                        "location_type": "ROOFTOP",
                    },
                    "address_components": [
                        {"types": ["street_number"], "long_name": "1"},
                        {"types": ["route"], "long_name": "Хрещатик"},
                    ],
                }
            ]
        }
        response.raise_for_status = MagicMock()
        http_client.get.return_value = response

        result = await client.geocode("Хрещатик", "1", "Київ")

        assert result == CoordinatesDTO(latitude=50.45, longitude=30.52)
        pipeline_mock.execute.assert_awaited_once()

    @pytest.mark.asyncio()
    async def test_monthly_limit_reached(self, client, http_client, redis):
        redis.get.return_value = str(FREE_MONTHLY_LIMIT)

        result = await client.geocode("Хрещатик", "1", "Київ")

        assert result is None
        http_client.get.assert_not_awaited()

    @pytest.mark.asyncio()
    async def test_http_error(self, client, http_client, redis):
        redis.get.return_value = None

        mock_response = MagicMock()
        mock_response.status_code = 500
        http_client.get.side_effect = httpx.HTTPStatusError(
            "Server Error", request=MagicMock(), response=mock_response
        )

        result = await client.geocode("Хрещатик", "1", "Київ")

        assert result is None

    @pytest.mark.asyncio()
    async def test_empty_results(self, client, http_client, redis):
        redis.get.return_value = None

        response = MagicMock()
        response.json.return_value = {"results": []}
        response.raise_for_status = MagicMock()
        http_client.get.return_value = response

        result = await client.geocode("Невідома", "999", "Місто")

        assert result is None

    @pytest.mark.asyncio()
    async def test_parse_error(self, client, http_client, redis):
        redis.get.return_value = None

        response = MagicMock()
        response.json.return_value = {"results": [{"geometry": {}}]}
        response.raise_for_status = MagicMock()
        http_client.get.return_value = response

        result = await client.geocode("Хрещатик", "1", "Київ")

        assert result is None

    @pytest.mark.asyncio()
    async def test_approximate_result_rejected(
        self, client, http_client, redis
    ):
        redis.get.return_value = None

        response = MagicMock()
        response.json.return_value = {
            "results": [
                {
                    "geometry": {
                        "location": {"lat": "50.45", "lng": "30.52"},
                        "location_type": "APPROXIMATE",
                    },
                }
            ]
        }
        response.raise_for_status = MagicMock()
        http_client.get.return_value = response

        result = await client.geocode("Хрещатик", "1", "Київ")

        assert result is None

    @pytest.mark.asyncio()
    async def test_missing_street_number_rejected(
        self, client, http_client, redis
    ):
        redis.get.return_value = None

        response = MagicMock()
        response.json.return_value = {
            "results": [
                {
                    "geometry": {
                        "location": {"lat": "50.45", "lng": "30.52"},
                        "location_type": "GEOMETRIC_CENTER",
                    },
                    "address_components": [
                        {"types": ["route"], "long_name": "Хрещатик"},
                    ],
                }
            ]
        }
        response.raise_for_status = MagicMock()
        http_client.get.return_value = response

        result = await client.geocode("Хрещатик", "1", "Київ")

        assert result is None


class TestEmptyApiKey:
    @pytest.mark.asyncio()
    async def test_geocode_skipped(self, http_client, redis):
        cfg = MagicMock()
        cfg.api_key = ""
        client = GoogleGeocoderClient(
            http_client=http_client, config=cfg, redis=redis
        )

        result = await client.geocode("Хрещатик", "1", "Київ")

        assert result is None
        http_client.get.assert_not_called()

    @pytest.mark.asyncio()
    async def test_reverse_skipped(self, http_client, redis):
        cfg = MagicMock()
        cfg.api_key = ""
        client = GoogleGeocoderClient(
            http_client=http_client, config=cfg, redis=redis
        )

        result = await client.reverse(
            CoordinatesDTO(latitude=50.45, longitude=30.52)
        )

        assert result is None
        http_client.get.assert_not_called()

    @pytest.mark.asyncio()
    async def test_suggest_skipped(self, http_client, redis):
        cfg = MagicMock()
        cfg.api_key = ""
        client = GoogleGeocoderClient(
            http_client=http_client, config=cfg, redis=redis
        )

        result = await client.suggest("Хрещатик", "Київ")

        assert result == []
        http_client.get.assert_not_called()


class TestSuggest:
    @pytest.mark.asyncio()
    async def test_prioritizes_house_number_and_normalizes(
        self, client, http_client, redis
    ):
        redis.get.return_value = None
        redis.ttl.return_value = -2
        pipeline_mock = MagicMock()
        pipeline_mock.execute = AsyncMock()
        redis.pipeline = MagicMock(return_value=pipeline_mock)

        response = MagicMock()
        response.json.return_value = {
            "results": [
                {
                    "formatted_address": "Хрещатик, Київ, Україна",
                    "geometry": {
                        "location": {"lat": "50.4500", "lng": "30.5200"},
                        "location_type": "GEOMETRIC_CENTER",
                    },
                    "address_components": [
                        {"types": ["route"], "long_name": "Хрещатик"},
                        {"types": ["locality"], "long_name": "Київ"},
                    ],
                },
                {
                    "formatted_address": "Хрещатик 1, Київ, Україна",
                    "geometry": {
                        "location": {"lat": "50.4501", "lng": "30.5234"},
                        "location_type": "ROOFTOP",
                    },
                    "address_components": [
                        {"types": ["street_number"], "long_name": "1"},
                        {"types": ["route"], "long_name": "Хрещатик"},
                        {"types": ["locality"], "long_name": "Київ"},
                    ],
                },
            ]
        }
        response.raise_for_status = MagicMock()
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
            ),
        ]
        pipeline_mock.execute.assert_awaited_once()

    @pytest.mark.asyncio()
    async def test_falls_back_cleanly_when_metadata_is_incomplete(
        self, client, http_client, redis
    ):
        redis.get.return_value = None
        redis.ttl.return_value = -2
        pipeline_mock = MagicMock()
        pipeline_mock.execute = AsyncMock()
        redis.pipeline = MagicMock(return_value=pipeline_mock)

        response = MagicMock()
        response.json.return_value = {
            "results": [
                {
                    "geometry": {
                        "location": {"lat": "50.4501", "lng": "30.5234"},
                        "location_type": "ROOFTOP",
                    },
                    "address_components": [
                        {"types": ["street_number"], "long_name": "1"},
                        {"types": ["route"], "long_name": "Хрещатик"},
                    ],
                }
            ]
        }
        response.raise_for_status = MagicMock()
        http_client.get.return_value = response

        result = await client.suggest("Хрещатик", "Київ")

        assert result == []
        pipeline_mock.execute.assert_awaited_once()

    @pytest.mark.asyncio()
    async def test_non_positive_limit_skips_request(
        self, client, http_client, redis
    ):
        result = await client.suggest("Хрещатик", "Київ", limit=0)

        assert result == []
        http_client.get.assert_not_awaited()

    @pytest.mark.asyncio()
    async def test_empty_results_still_count_request(
        self, client, http_client, redis
    ):
        redis.get.return_value = None
        redis.ttl.return_value = -2
        pipeline_mock = MagicMock()
        pipeline_mock.execute = AsyncMock()
        redis.pipeline = MagicMock(return_value=pipeline_mock)

        response = MagicMock()
        response.json.return_value = {"results": []}
        response.raise_for_status = MagicMock()
        http_client.get.return_value = response

        result = await client.suggest("Хрещатик", "Київ")

        assert result == []
        pipeline_mock.execute.assert_awaited_once()

    @pytest.mark.asyncio()
    async def test_monthly_limit_reached(self, client, http_client, redis):
        redis.get.return_value = str(FREE_MONTHLY_LIMIT)

        result = await client.suggest("Хрещатик", "Київ")

        assert result == []
        http_client.get.assert_not_awaited()
