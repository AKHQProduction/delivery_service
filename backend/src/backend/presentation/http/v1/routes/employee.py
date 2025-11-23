from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer

from backend.application.commands import (
    DeleteEmployeeCommand,
    DeleteEmployeeCommandHandler,
    EditEmployeeCommand,
    EditEmployeeCommandHandler,
)
from backend.application.interfaces.gateways import Pagination, SortOrder
from backend.application.interfaces.gateways.shop_gateway import (
    EmployeeReadModel,
)
from backend.application.queries.get_employee import GetEmployeeQueryHandler
from backend.application.queries.get_employees import (
    GetEmployeesQuery,
    GetEmployeesQueryHandler,
)
from backend.application.vars import UserId
from backend.presentation.http.v1.schemas.employee import EditEmployeeSchema
from backend.presentation.http.v1.schemas.error import ErrorSchema

router = APIRouter(
    prefix="/employee", tags=["Employee"], route_class=DishkaRoute
)


@router.patch(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
        status.HTTP_403_FORBIDDEN: {"model": ErrorSchema},
        status.HTTP_404_NOT_FOUND: {"model": ErrorSchema},
    },
    dependencies=[Depends(HTTPBearer())],
)
async def update_employee(
    user_id: UserId,
    body: EditEmployeeSchema,
    handler: FromDishka[EditEmployeeCommandHandler],
) -> None:
    return await handler.handle(
        EditEmployeeCommand(
            user_id=user_id, new_name=body.name, new_role=body.role
        )
    )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
        status.HTTP_403_FORBIDDEN: {"model": ErrorSchema},
        status.HTTP_404_NOT_FOUND: {"model": ErrorSchema},
    },
    dependencies=[Depends(HTTPBearer())],
)
async def delete_employee(
    user_id: UserId,
    handler: FromDishka[DeleteEmployeeCommandHandler],
) -> None:
    return await handler.handle(DeleteEmployeeCommand(user_id=user_id))


@router.get(
    "/all",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
    },
    dependencies=[Depends(HTTPBearer())],
)
async def get_all_employees(
    handler: FromDishka[GetEmployeesQueryHandler],
    name: str | None = None,
    limit: int = 100,
    offset: int = 0,
    order: SortOrder = SortOrder.ASC,
) -> list[EmployeeReadModel]:
    return await handler.handle(
        GetEmployeesQuery(
            name=name,
            pagination=Pagination(limit=limit, offset=offset, order=order),
        )
    )


@router.get(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
        status.HTTP_404_NOT_FOUND: {"model": ErrorSchema},
    },
    dependencies=[Depends(HTTPBearer())],
)
async def get_employee(
    user_id: UserId, handler: FromDishka[GetEmployeeQueryHandler]
) -> EmployeeReadModel:
    return await handler.handle(user_id=user_id)
