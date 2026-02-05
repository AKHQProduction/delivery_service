from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Body, Depends, status
from fastapi.openapi.models import Example
from fastapi.security import HTTPBearer

from backend.application.commands.edit_shop import (
    EditShopCommand,
    EditShopCommandHandler,
)
from backend.presentation.http.v1.schemas.error import (
    ErrorSchema,
)

router = APIRouter(
    prefix="/shop",
    tags=["Shop"],
    route_class=DishkaRoute,
)

_EDIT_SHOP_EXAMPLES: dict[str, Example] = {
    "update_address": Example(
        summary="Update shop address",
        description=(
            "Address must be sent in full — all fields are required."
        ),
        value={
            "address": {
                "city": "Moscow",
                "street": "Lenina",
                "house": "10",
                "coordinates": {
                    "latitude": 55.7558,
                    "longitude": 37.6173,
                },
            }
        },
    ),
}


@router.patch(
    "",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorSchema,
        },
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorSchema,
        },
    },
    dependencies=[Depends(HTTPBearer())],
)
async def update_shop(
    body: Annotated[
        EditShopCommand,
        Body(openapi_examples=_EDIT_SHOP_EXAMPLES),
    ],
    handler: FromDishka[EditShopCommandHandler],
) -> None:
    await handler.handle(body)
