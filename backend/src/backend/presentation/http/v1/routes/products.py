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
from backend.application.interfaces.gateways import Pagination, SortOrder
from backend.application.interfaces.gateways.product_gateway import (
    ProductReadModel,
)
from backend.application.queries.get_product import GetProductQueryHandler
from backend.application.queries.get_products import (
    GetProductQuery,
    GetProductsQueryHandler,
)
from backend.application.vars import CategoryId, ProductId
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
                "without_category": Example(
                    description="Create new product without category",
                    value={
                        "name": "Test Product",
                        "price": 100,
                    },
                ),
                "with_category": Example(
                    description="Create new product with category",
                    value={
                        "name": "Test Product",
                        "price": 100,
                        "category_id": "550e8400-e29b-41d4-a716-446655440000",
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
        status.HTTP_404_NOT_FOUND: {"model": ErrorSchema},
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
            new_category_id=CategoryId(body.category_id)
            if body.category_id
            else None,
        )
    )


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
        status.HTTP_403_FORBIDDEN: {"model": ErrorSchema},
        status.HTTP_404_NOT_FOUND: {"model": ErrorSchema},
    },
    dependencies=[Depends(HTTPBearer())],
)
async def delete_product(
    product_id: ProductId, handler: FromDishka[DeleteProductCommandHandler]
) -> None:
    await handler.handle(DeleteProductCommand(product_id=product_id))


@router.get(
    "/all",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
    },
    dependencies=[Depends(HTTPBearer())],
)
async def get_all_products(
    handler: FromDishka[GetProductsQueryHandler],
    name: str | None = None,
    limit: int = 100,
    offset: int = 0,
    order: SortOrder = SortOrder.ASC,
) -> list[ProductReadModel]:
    return await handler.handle(
        GetProductQuery(
            name=name,
            pagination=Pagination(limit=limit, offset=offset, order=order),
        )
    )


@router.get(
    "/{product_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
        status.HTTP_404_NOT_FOUND: {"model": ErrorSchema},
    },
    dependencies=[Depends(HTTPBearer())],
)
async def get_product(
    product_id: ProductId, handler: FromDishka[GetProductQueryHandler]
) -> ProductReadModel:
    return await handler.handle(product_id=product_id)
