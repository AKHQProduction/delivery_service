from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer

from backend.application.dto.coordinates import CoordinatesDTO
from backend.infrastructure.nominatim import NominatimClient
from backend.presentation.http.v1.schemas.error import ErrorSchema

router = APIRouter(
    prefix="/geocoding", tags=["Geocoding"], route_class=DishkaRoute
)


@router.get(
    "/forward",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
    },
    dependencies=[Depends(HTTPBearer(auto_error=False))],
)
async def forward_geocode(
    street: str,
    house: str,
    city: str,
    client: FromDishka[NominatimClient],
) -> CoordinatesDTO | None:
    return await client.geocode(street, house, city)


@router.get(
    "/reverse",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
    },
    dependencies=[Depends(HTTPBearer(auto_error=False))],
)
async def reverse_geocode(
    lat: float,
    lon: float,
    client: FromDishka[NominatimClient],
) -> dict | None:
    return await client.reverse_raw(
        CoordinatesDTO(latitude=lat, longitude=lon)
    )
