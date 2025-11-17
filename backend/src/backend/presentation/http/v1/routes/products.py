from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Body, Depends, status
from fastapi.openapi.models import Example
from fastapi.security import HTTPBearer

from backend.application.commands.create_product import (
    CreateProductCommand,
    CreateProductCommandHandler,
)
from backend.application.vars import ProductCategory, ProductId
from backend.presentation.http.v1.schemas.error import ErrorSchema

router = APIRouter(
    prefix="/products", tags=["Products"], route_class=DishkaRoute
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    responses={status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema}},
    dependencies=[Depends(HTTPBearer())],
)
async def create_new_product(
    body: Annotated[
        CreateProductCommand,
        Body(
            openapi_examples={
                "water": Example(
                    description="Create new product with water category",
                    value={
                        "name": "Test Product",
                        "price": 100,
                        "category": ProductCategory.WATER,
                    },
                ),
                "other": Example(
                    description="Create new product with other category",
                    value={
                        "name": "Test Other Product",
                        "price": 100,
                        "category": ProductCategory.OTHER,
                    },
                ),
            }
        ),
    ],
    handler: FromDishka[CreateProductCommandHandler],
) -> ProductId:
    return await handler.handle(body)
