from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer

from backend.application.dto.coordinates import (
    CoordinatesDTO,
    ReverseGeocodeResult,
)
from backend.application.services.geocoder import Geocoder
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
    geocoder: FromDishka[Geocoder],
) -> CoordinatesDTO | None:
    return await geocoder.geocode(street, house, city)


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
    geocoder: FromDishka[Geocoder],
) -> ReverseGeocodeResult | None:
    return await geocoder.reverse(CoordinatesDTO(latitude=lat, longitude=lon))
