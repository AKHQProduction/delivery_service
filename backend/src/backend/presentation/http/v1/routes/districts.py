from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Body, Depends, status
from fastapi.security import HTTPBearer

from backend.application.commands.create_district import (
    CreateDistrictCommand,
    CreateDistrictCommandHandler,
)
from backend.application.commands.delete_district import (
    DeleteDistrictCommand,
    DeleteDistrictCommandHandler,
)
from backend.application.commands.edit_district import (
    EditDistrictCommand,
    EditDistrictCommandHandler,
)
from backend.application.dto.gateways import Pagination, SortOrder
from backend.application.dto.gateways.district_gateway import (
    DistrictReadModel,
)
from backend.application.queries.get_districts import (
    GetDistrictsQuery,
    GetDistrictsQueryHandler,
)
from backend.application.vars import DistrictId
from backend.presentation.http.v1.schemas.district import EditDistrictSchema
from backend.presentation.http.v1.schemas.error import ErrorSchema

router = APIRouter(
    prefix="/districts", tags=["Districts"], route_class=DishkaRoute
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
        status.HTTP_409_CONFLICT: {"model": ErrorSchema},
    },
    dependencies=[Depends(HTTPBearer())],
)
async def create_district(
    body: Annotated[CreateDistrictCommand, Body()],
    handler: FromDishka[CreateDistrictCommandHandler],
) -> DistrictId:
    return await handler.handle(body)


@router.patch(
    "/{district_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
        status.HTTP_403_FORBIDDEN: {"model": ErrorSchema},
        status.HTTP_404_NOT_FOUND: {"model": ErrorSchema},
        status.HTTP_409_CONFLICT: {"model": ErrorSchema},
    },
    dependencies=[Depends(HTTPBearer())],
)
async def update_district(
    district_id: DistrictId,
    body: EditDistrictSchema,
    handler: FromDishka[EditDistrictCommandHandler],
) -> None:
    await handler.handle(
        EditDistrictCommand(
            district_id=district_id,
            new_name=body.name,
        )
    )


@router.delete(
    "/{district_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
        status.HTTP_403_FORBIDDEN: {"model": ErrorSchema},
    },
    dependencies=[Depends(HTTPBearer())],
)
async def delete_district(
    district_id: DistrictId,
    handler: FromDishka[DeleteDistrictCommandHandler],
) -> None:
    await handler.handle(DeleteDistrictCommand(district_id=district_id))


@router.get(
    "/all",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
    },
    dependencies=[Depends(HTTPBearer())],
)
async def get_all_districts(
    handler: FromDishka[GetDistrictsQueryHandler],
    name: str | None = None,
    limit: int = 100,
    offset: int = 0,
    order: SortOrder = SortOrder.ASC,
) -> list[DistrictReadModel]:
    return await handler.handle(
        GetDistrictsQuery(
            name=name,
            pagination=Pagination(limit=limit, offset=offset, order=order),
        )
    )
