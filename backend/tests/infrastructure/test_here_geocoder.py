from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from backend.application.dto.coordinates import (
    AddressSuggestionDTO,
    CoordinatesDTO,
    ReverseGeocodeResult,
)
from backend.infrastructure.geocoding.here_geocoder import (
    FREE_MONTHLY_LIMIT,
    HereGeocoderClient,
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
    return HereGeocoderClient(
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
            "items": [
                {
                    "resultType": "houseNumber",
                    "address": {"houseNumber": "1"},
                    "position": {"lat": 50.45, "lng": 30.52},
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
        mock_response.status_code = 401
        http_client.get.side_effect = httpx.HTTPStatusError(
            "Unauthorized", request=MagicMock(), response=mock_response
        )

        result = await client.geocode("Хрещатик", "1", "Київ")

        assert result is None

    @pytest.mark.asyncio()
    async def test_empty_items(self, client, http_client, redis):
        redis.get.return_value = None

        response = MagicMock()
        response.json.return_value = {"items": []}
        response.raise_for_status = MagicMock()
        http_client.get.return_value = response

        result = await client.geocode("Невідома", "999", "Місто")

        assert result is None

    @pytest.mark.asyncio()
    async def test_parse_error(self, client, http_client, redis):
        redis.get.return_value = None

        response = MagicMock()
        response.json.return_value = {"items": [{"position": {}}]}
        response.raise_for_status = MagicMock()
        http_client.get.return_value = response

        result = await client.geocode("Хрещатик", "1", "Київ")

        assert result is None

    @pytest.mark.asyncio()
    async def test_vague_result_rejected(self, client, http_client, redis):
        redis.get.return_value = None

        response = MagicMock()
        response.json.return_value = {
            "items": [
                {
                    "resultType": "locality",
                    "address": {"city": "Київ"},
                    "position": {"lat": 50.45, "lng": 30.52},
                }
            ]
        }
        response.raise_for_status = MagicMock()
        http_client.get.return_value = response

        result = await client.geocode("Хрещатик", "1", "Київ")

        assert result is None

    @pytest.mark.asyncio()
    async def test_missing_house_number_rejected(
        self, client, http_client, redis
    ):
        redis.get.return_value = None

        response = MagicMock()
        response.json.return_value = {
            "items": [
                {
                    "resultType": "street",
                    "address": {"street": "Хрещатик"},
                    "position": {"lat": 50.45, "lng": 30.52},
                }
            ]
        }
        response.raise_for_status = MagicMock()
        http_client.get.return_value = response

        result = await client.geocode("Хрещатик", "1", "Київ")

        assert result is None


class TestReverse:
    @pytest.mark.asyncio()
    async def test_success(self, client, http_client, redis):
        redis.get.return_value = None
        redis.ttl.return_value = 86000
        pipeline_mock = MagicMock()
        pipeline_mock.execute = AsyncMock()
        redis.pipeline = MagicMock(return_value=pipeline_mock)

        response = MagicMock()
        response.json.return_value = {
            "items": [
                {
                    "title": "Хрещатик 1, Київ",
                    "address": {
                        "label": "Хрещатик 1, 01001 Київ, Україна",
                        "street": "Хрещатик",
                        "houseNumber": "1",
                        "city": "Київ",
                        "district": "Шевченківський",
                    },
                }
            ]
        }
        response.raise_for_status = MagicMock()
        http_client.get.return_value = response

        result = await client.reverse(
            CoordinatesDTO(latitude=50.45, longitude=30.52)
        )

        assert result == ReverseGeocodeResult(
            display_name="Хрещатик 1, 01001 Київ, Україна",
            street="Хрещатик",
            house="1",
            city="Київ",
            district="Шевченківський",
        )

    @pytest.mark.asyncio()
    async def test_monthly_limit_reached(self, client, http_client, redis):
        redis.get.return_value = str(FREE_MONTHLY_LIMIT)

        result = await client.reverse(
            CoordinatesDTO(latitude=50.45, longitude=30.52)
        )

        assert result is None
        http_client.get.assert_not_awaited()

    @pytest.mark.asyncio()
    async def test_filters_district_when_it_matches_city(
        self, client, http_client, redis
    ):
        redis.get.return_value = None
        redis.ttl.return_value = 86000
        pipeline_mock = MagicMock()
        pipeline_mock.execute = AsyncMock()
        redis.pipeline = MagicMock(return_value=pipeline_mock)

        response = MagicMock()
        response.json.return_value = {
            "items": [
                {
                    "title": "Надпільна вулиця, 242, Черкаси, Україна",
                    "address": {
                        "label": "Надпільна вулиця, 242, Черкаси, Україна",
                        "street": "Надпільна вулиця",
                        "houseNumber": "242",
                        "city": "Черкаси",
                        "district": "Черкаси",
                    },
                }
            ]
        }
        response.raise_for_status = MagicMock()
        http_client.get.return_value = response

        result = await client.reverse(
            CoordinatesDTO(latitude=49.4335, longitude=32.0637)
        )

        assert result == ReverseGeocodeResult(
            display_name="Надпільна вулиця, 242, Черкаси, Україна",
            street="Надпільна вулиця",
            house="242",
            city="Черкаси",
            district=None,
        )

    @pytest.mark.asyncio()
    async def test_empty_items(self, client, http_client, redis):
        redis.get.return_value = None

        response = MagicMock()
        response.json.return_value = {"items": []}
        response.raise_for_status = MagicMock()
        http_client.get.return_value = response

        result = await client.reverse(
            CoordinatesDTO(latitude=50.45, longitude=30.52)
        )

        assert result is None


class TestEmptyApiKey:
    @pytest.mark.asyncio()
    async def test_geocode_skipped(self, http_client, redis):
        cfg = MagicMock()
        cfg.api_key = ""
        client = HereGeocoderClient(
            http_client=http_client, config=cfg, redis=redis
        )

        result = await client.geocode("Хрещатик", "1", "Київ")

        assert result is None
        http_client.get.assert_not_called()

    @pytest.mark.asyncio()
    async def test_reverse_skipped(self, http_client, redis):
        cfg = MagicMock()
        cfg.api_key = ""
        client = HereGeocoderClient(
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
        client = HereGeocoderClient(
            http_client=http_client, config=cfg, redis=redis
        )

        result = await client.suggest("Хрещатик", "Київ")

        assert result == []
        http_client.get.assert_not_called()


class TestSuggest:
    @pytest.mark.asyncio()
    async def test_prioritizes_house_number_before_limit(
        self, client, http_client, redis
    ):
        redis.get.return_value = None
        redis.ttl.return_value = -2
        pipeline_mock = MagicMock()
        pipeline_mock.execute = AsyncMock()
        redis.pipeline = MagicMock(return_value=pipeline_mock)

        response = MagicMock()
        response.json.return_value = {
            "items": [
                {
                    "resultType": "street",
                    "title": "Хрещатик, Київ",
                    "address": {
                        "label": "Хрещатик, Київ, Україна",
                        "street": "Хрещатик",
                        "city": "Київ",
                    },
                    "position": {"lat": 50.4500, "lng": 30.5200},
                },
                {
                    "resultType": "houseNumber",
                    "title": "Хрещатик 1, Київ",
                    "address": {
                        "label": "Хрещатик 1, 01001 Київ, Україна",
                        "street": "Хрещатик",
                        "houseNumber": "1",
                        "city": "Київ",
                    },
                    "position": {"lat": 50.4501, "lng": 30.5234},
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
            )
        ]
        http_client.get.assert_awaited_once()
        assert http_client.get.await_args.kwargs["params"]["limit"] == "10"
        pipeline_mock.execute.assert_awaited_once()

    @pytest.mark.asyncio()
    async def test_normalizes_street_only_item_without_house(
        self, client, http_client, redis
    ):
        redis.get.return_value = None
        redis.ttl.return_value = -2
        pipeline_mock = MagicMock()
        pipeline_mock.execute = AsyncMock()
        redis.pipeline = MagicMock(return_value=pipeline_mock)

        response = MagicMock()
        response.json.return_value = {
            "items": [
                {
                    "resultType": "street",
                    "title": "Хрещатик, Київ",
                    "address": {
                        "label": "Хрещатик, Київ, Україна",
                        "street": "Хрещатик",
                        "city": "Київ",
                    },
                    "position": {"lat": 50.4501, "lng": 30.5234},
                }
            ]
        }
        response.raise_for_status = MagicMock()
        http_client.get.return_value = response

        result = await client.suggest("Хрещатик", "Київ")

        assert result == [
            AddressSuggestionDTO(
                label="Хрещатик, Київ",
                street="Хрещатик",
                house="",
                city="Київ",
                coordinates=CoordinatesDTO(
                    latitude=50.4501, longitude=30.5234
                ),
            )
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
            "items": [
                {
                    "resultType": "houseNumber",
                    "address": {"street": "Хрещатик", "houseNumber": "1"},
                    "position": {"lat": 50.4501, "lng": 30.5234},
                }
            ]
        }
        response.raise_for_status = MagicMock()
        http_client.get.return_value = response

        result = await client.suggest("Хрещатик", "Київ")

        assert result == []
        pipeline_mock.execute.assert_awaited_once()

    @pytest.mark.asyncio()
    async def test_rejects_non_addressish_item_and_counts_request(
        self, client, http_client, redis
    ):
        redis.get.return_value = None
        redis.ttl.return_value = -2
        pipeline_mock = MagicMock()
        pipeline_mock.execute = AsyncMock()
        redis.pipeline = MagicMock(return_value=pipeline_mock)

        response = MagicMock()
        response.json.return_value = {
            "items": [
                {
                    "resultType": "locality",
                    "address": {
                        "street": "Київ",
                        "city": "Київ",
                    },
                    "position": {"lat": 50.4501, "lng": 30.5234},
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
    async def test_monthly_limit_reached(self, client, http_client, redis):
        redis.get.return_value = str(FREE_MONTHLY_LIMIT)

        result = await client.suggest("Хрещатик", "Київ")

        assert result == []
        http_client.get.assert_not_awaited()
