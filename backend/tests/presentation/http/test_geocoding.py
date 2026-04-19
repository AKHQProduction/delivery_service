from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status
from httpx import AsyncClient

from backend.application.dto.coordinates import (
    AddressSuggestionDTO,
    CoordinatesDTO,
)

BASE_URL = "/api/v1/geocoding/suggest"


@pytest.mark.asyncio()
async def test_suggest_returns_normalized_items(
    http_client: AsyncClient,
) -> None:
    suggestions = [
        AddressSuggestionDTO(
            label="Хрещатик, 1, Київ",
            street="Хрещатик",
            house="1",
            city="Київ",
            coordinates=CoordinatesDTO(latitude=50.4501, longitude=30.5234),
        )
    ]

    with patch(
        "backend.application.services.geocoder.Geocoder.suggest",
        new_callable=AsyncMock,
        return_value=suggestions,
    ):
        response = await http_client.get(
            url=BASE_URL,
            params={"query": "Хрещатик", "city": "Київ"},
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            "label": "Хрещатик, 1, Київ",
            "street": "Хрещатик",
            "house": "1",
            "city": "Київ",
            "coordinates": {
                "latitude": 50.4501,
                "longitude": 30.5234,
            },
        }
    ]


@pytest.mark.asyncio()
async def test_suggest_returns_empty_list(
    http_client: AsyncClient,
) -> None:
    with patch(
        "backend.application.services.geocoder.Geocoder.suggest",
        new_callable=AsyncMock,
        return_value=[],
    ):
        response = await http_client.get(
            url=BASE_URL,
            params={"query": "Невідомо", "city": "Київ"},
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


@pytest.mark.asyncio()
async def test_suggest_defaults_limit_to_5(
    http_client: AsyncClient,
) -> None:
    with patch(
        "backend.application.services.geocoder.Geocoder.suggest",
        new_callable=AsyncMock,
        return_value=[],
    ) as mock_suggest:
        response = await http_client.get(
            url=BASE_URL,
            params={"query": "Хрещатик", "city": "Київ"},
        )

    assert response.status_code == status.HTTP_200_OK
    mock_suggest.assert_awaited_once_with(
        query="Хрещатик", city="Київ", limit=5
    )


@pytest.mark.asyncio()
async def test_suggest_rejects_non_positive_limit(
    http_client: AsyncClient,
) -> None:
    response = await http_client.get(
        url=BASE_URL,
        params={"query": "Хрещатик", "city": "Київ", "limit": 0},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
