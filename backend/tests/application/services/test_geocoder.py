from unittest.mock import AsyncMock

import pytest

from backend.application.dto.coordinates import (
    AddressSuggestionDTO,
    CoordinatesDTO,
)
from backend.application.services.geocoder import Geocoder
from backend.application.vars import Empty


@pytest.fixture()
def coords():
    return CoordinatesDTO(latitude=50.4501, longitude=30.5234)


@pytest.fixture()
def cache():
    return AsyncMock()


@pytest.fixture()
def provider_a():
    return AsyncMock()


@pytest.fixture()
def provider_b():
    return AsyncMock()


@pytest.fixture()
def geocoder(cache, provider_a, provider_b):
    return Geocoder(cache=cache, providers=[provider_a, provider_b])


class TestGeocode:
    @pytest.mark.asyncio()
    async def test_cache_hit(
        self, geocoder, cache, provider_a, provider_b, coords
    ):
        cache.get.return_value = coords

        result = await geocoder.geocode("Хрещатик", "1", "Київ")

        assert result == coords
        cache.get.assert_awaited_once_with("Київ", "Хрещатик", "1")
        provider_a.geocode.assert_not_awaited()
        provider_b.geocode.assert_not_awaited()

    @pytest.mark.asyncio()
    async def test_first_provider_succeeds(
        self, geocoder, cache, provider_a, provider_b, coords
    ):
        cache.get.return_value = None
        provider_a.geocode.return_value = coords

        result = await geocoder.geocode("Хрещатик", "1", "Київ")

        assert result == coords
        provider_a.geocode.assert_awaited_once_with(
            "Хрещатик", "1", "Київ", require_house=True
        )
        provider_b.geocode.assert_not_awaited()
        cache.set.assert_awaited_once_with("Київ", "Хрещатик", "1", coords)

    @pytest.mark.asyncio()
    async def test_falls_through_to_second_provider(
        self, geocoder, cache, provider_a, provider_b, coords
    ):
        cache.get.return_value = None
        provider_a.geocode.return_value = None
        provider_b.geocode.return_value = coords

        result = await geocoder.geocode("Хрещатик", "1", "Київ")

        assert result == coords
        provider_a.geocode.assert_awaited_once_with(
            "Хрещатик", "1", "Київ", require_house=True
        )
        provider_b.geocode.assert_awaited_once_with(
            "Хрещатик", "1", "Київ", require_house=True
        )
        cache.set.assert_awaited_once_with("Київ", "Хрещатик", "1", coords)

    @pytest.mark.asyncio()
    async def test_all_providers_fail(
        self, geocoder, cache, provider_a, provider_b
    ):
        cache.get.return_value = None
        provider_a.geocode.return_value = None
        provider_b.geocode.return_value = None

        result = await geocoder.geocode("Невідома", "999", "Місто")

        assert result is None
        cache.set.assert_not_awaited()
        cache.set_not_found.assert_awaited_once_with(
            "Місто", "Невідома", "999"
        )

    @pytest.mark.asyncio()
    async def test_negative_cache_hit(
        self, geocoder, cache, provider_a, provider_b
    ):
        cache.get.return_value = Empty.EMPTY

        result = await geocoder.geocode("Невідома", "999", "Місто")

        assert result is None
        provider_a.geocode.assert_not_awaited()
        provider_b.geocode.assert_not_awaited()


class TestGeocodeIfMissing:
    @pytest.mark.asyncio()
    async def test_returns_existing_coordinates(
        self, geocoder, cache, provider_a, coords
    ):
        result = await geocoder.geocode_if_missing(
            street="Хрещатик",
            house="1",
            coordinates=coords,
            shop_city="Київ",
        )

        assert result == coords
        cache.get.assert_not_awaited()
        provider_a.geocode.assert_not_awaited()

    @pytest.mark.asyncio()
    async def test_returns_none_when_no_city(
        self, geocoder, cache, provider_a
    ):
        result = await geocoder.geocode_if_missing(
            street="Хрещатик",
            house="1",
            coordinates=None,
            shop_city=None,
        )

        assert result is None
        cache.get.assert_not_awaited()
        provider_a.geocode.assert_not_awaited()

    @pytest.mark.asyncio()
    async def test_delegates_to_geocode(
        self, geocoder, cache, provider_a, coords
    ):
        cache.get.return_value = None
        provider_a.geocode.return_value = coords

        result = await geocoder.geocode_if_missing(
            street="Хрещатик",
            house="1",
            coordinates=None,
            shop_city="Київ",
        )

        assert result == coords
        cache.get.assert_awaited_once()
        provider_a.geocode.assert_awaited_once_with(
            "Хрещатик", "1", "Київ", require_house=True
        )


class TestSuggest:
    @pytest.mark.asyncio()
    async def test_first_provider_succeeds(
        self, geocoder, provider_a, provider_b
    ):
        suggestions = [
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
        provider_a.suggest.return_value = suggestions
        provider_b.suggest.return_value = []

        result = await geocoder.suggest("Хрещатик", "Київ")

        assert result == suggestions
        provider_a.suggest.assert_awaited_once_with(
            "Хрещатик", "Київ", limit=5
        )
        provider_b.suggest.assert_not_awaited()

    @pytest.mark.asyncio()
    async def test_falls_through_to_second_provider(
        self, geocoder, provider_a, provider_b
    ):
        suggestions = [
            AddressSuggestionDTO(
                label="Хрещатик, 1, Київ",
                street="Хрещатик",
                house="1",
                city="Київ",
                coordinates=None,
            )
        ]
        provider_a.suggest.return_value = []
        provider_b.suggest.return_value = suggestions

        result = await geocoder.suggest("Хрещатик", "Київ", limit=3)

        assert result == suggestions
        provider_a.suggest.assert_awaited_once_with(
            "Хрещатик", "Київ", limit=3
        )
        provider_b.suggest.assert_awaited_once_with(
            "Хрещатик", "Київ", limit=3
        )

    @pytest.mark.asyncio()
    async def test_non_positive_limit_skips_providers(
        self, geocoder, provider_a, provider_b
    ):
        result = await geocoder.suggest("Хрещатик", "Київ", limit=0)

        assert result == []
        provider_a.suggest.assert_not_awaited()
        provider_b.suggest.assert_not_awaited()

    @pytest.mark.asyncio()
    async def test_dedupes_same_address_from_provider(
        self, geocoder, provider_a, provider_b
    ):
        provider_a.suggest.return_value = [
            AddressSuggestionDTO(
                label="Надпільна вулиця, 252, Мікрорайон Соборний, Черкаси",
                street="Надпільна вулиця",
                house="252",
                city="Черкаси",
                district="Мікрорайон Соборний",
                coordinates=CoordinatesDTO(
                    latitude=49.4304, longitude=32.0682
                ),
            ),
            AddressSuggestionDTO(
                label="Надпільна вулиця, 252, Мікрорайон Соборний, Черкаси",
                street="Надпільна вулиця",
                house="252",
                city="Черкаси",
                district="Мікрорайон Соборний",
                coordinates=CoordinatesDTO(
                    latitude=49.4304, longitude=32.0677
                ),
            ),
        ]

        result = await geocoder.suggest("Надпільна 252", "Черкаси")

        assert len(result) == 1
        assert result[0].street == "Надпільна вулиця"
        provider_b.suggest.assert_not_awaited()
