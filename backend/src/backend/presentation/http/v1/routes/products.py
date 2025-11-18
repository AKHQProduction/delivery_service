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
from backend.application.commands.delete_product import (
    DeleteProductCommand,
    DeleteProductCommandHandler,
)
from backend.application.commands.edit_product import (
    EditProductCommand,
    EditProductCommandHandler,
)
from backend.application.interfaces.gateways.product_gateway import (
    ProductReadModel,
)
from backend.application.queries.get_product import GetProduct
from backend.application.vars import ProductCategory, ProductId
from backend.presentation.http.v1.schemas.error import ErrorSchema
from backend.presentation.http.v1.schemas.product import EditProductSchema

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


@router.patch(
    "/{product_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
        status.HTTP_403_FORBIDDEN: {"model": ErrorSchema},
    },
    dependencies=[Depends(HTTPBearer())],
)
async def update_product(
    product_id: ProductId,
    body: EditProductSchema,
    handler: FromDishka[EditProductCommandHandler],
) -> None:
    await handler.handle(
        EditProductCommand(
            product_id=product_id,
            new_name=body.name,
            new_price=body.price,
            new_category=body.category,
        )
    )


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
        status.HTTP_403_FORBIDDEN: {"model": ErrorSchema},
    },
    dependencies=[Depends(HTTPBearer())],
)
async def delete_product(
    product_id: ProductId, handler: FromDishka[DeleteProductCommandHandler]
) -> None:
    await handler.handle(DeleteProductCommand(product_id=product_id))


@router.get(
    "/{product_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
    },
    dependencies=[Depends(HTTPBearer())],
)
async def get_product(
    product_id: ProductId, handler: FromDishka[GetProduct]
) -> ProductReadModel:
    return await handler.handle(product_id=product_id)
