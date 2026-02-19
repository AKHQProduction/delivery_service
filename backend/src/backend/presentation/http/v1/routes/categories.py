from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Body, Depends, status
from fastapi.security import HTTPBearer

from backend.application.commands.create_category import (
    CreateCategoryCommand,
    CreateCategoryCommandHandler,
)
from backend.application.commands.delete_category import (
    DeleteCategoryCommand,
    DeleteCategoryCommandHandler,
)
from backend.application.commands.edit_category import (
    EditCategoryCommand,
    EditCategoryCommandHandler,
)
from backend.application.dto.gateways import Pagination, SortOrder
from backend.application.dto.gateways.category_gateway import (
    CategoryReadModel,
)
from backend.application.queries.get_categories import (
    GetCategoriesQuery,
    GetCategoriesQueryHandler,
)
from backend.application.vars import CategoryId
from backend.presentation.http.v1.schemas.category import EditCategorySchema
from backend.presentation.http.v1.schemas.error import ErrorSchema

router = APIRouter(
    prefix="/categories", tags=["Categories"], route_class=DishkaRoute
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
        status.HTTP_409_CONFLICT: {"model": ErrorSchema},
    },
    dependencies=[Depends(HTTPBearer(auto_error=False))],
)
async def create_category(
    body: Annotated[CreateCategoryCommand, Body()],
    handler: FromDishka[CreateCategoryCommandHandler],
) -> CategoryId:
    return await handler.handle(body)


@router.patch(
    "/{category_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
        status.HTTP_403_FORBIDDEN: {"model": ErrorSchema},
        status.HTTP_404_NOT_FOUND: {"model": ErrorSchema},
        status.HTTP_409_CONFLICT: {"model": ErrorSchema},
    },
    dependencies=[Depends(HTTPBearer(auto_error=False))],
)
async def update_category(
    category_id: CategoryId,
    body: EditCategorySchema,
    handler: FromDishka[EditCategoryCommandHandler],
) -> None:
    await handler.handle(
        EditCategoryCommand(
            category_id=category_id,
            new_name=body.name,
        )
    )


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
        status.HTTP_403_FORBIDDEN: {"model": ErrorSchema},
    },
    dependencies=[Depends(HTTPBearer(auto_error=False))],
)
async def delete_category(
    category_id: CategoryId,
    handler: FromDishka[DeleteCategoryCommandHandler],
) -> None:
    await handler.handle(DeleteCategoryCommand(category_id=category_id))


@router.get(
    "/all",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
    },
    dependencies=[Depends(HTTPBearer(auto_error=False))],
)
async def get_all_categories(
    handler: FromDishka[GetCategoriesQueryHandler],
    name: str | None = None,
    limit: int = 100,
    offset: int = 0,
    order: SortOrder = SortOrder.ASC,
) -> list[CategoryReadModel]:
    return await handler.handle(
        GetCategoriesQuery(
            name=name,
            pagination=Pagination(limit=limit, offset=offset, order=order),
        )
    )
