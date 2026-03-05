from datetime import date

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer

from backend.application.commands.reorder_route import (
    ReorderRouteCommand,
    ReorderRouteCommandHandler,
)
from backend.application.commands.reverse_route import (
    ReverseRouteCommand,
    ReverseRouteCommandHandler,
)
from backend.application.commands.update_order_coordinates import (
    UpdateOrderCoordinatesCommand,
    UpdateOrderCoordinatesCommandHandler,
)
from backend.application.dto.gateways.route_gateway import RouteReadModel
from backend.application.queries.get_route import (
    GetRouteQuery,
    GetRouteQueryHandler,
)
from backend.application.queries.get_shared_route import (
    GetSharedRouteQueryHandler,
)
from backend.application.vars import OrderId, RoutePlanId, TimeSlotId
from backend.presentation.http.v1.schemas.error import ErrorSchema
from backend.presentation.http.v1.schemas.route import UpdateCoordinatesSchema

router = APIRouter(prefix="/route", tags=["Route"], route_class=DishkaRoute)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
        status.HTTP_403_FORBIDDEN: {"model": ErrorSchema},
    },
    dependencies=[Depends(HTTPBearer(auto_error=False))],
)
async def get_route(
    delivery_date: date,
    handler: FromDishka[GetRouteQueryHandler],
    time_slot_id: TimeSlotId | None = None,
) -> RouteReadModel:
    return await handler.handle(
        GetRouteQuery(
            delivery_date=delivery_date,
            time_slot_id=time_slot_id,
        )
    )


@router.patch(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
        status.HTTP_403_FORBIDDEN: {"model": ErrorSchema},
        status.HTTP_404_NOT_FOUND: {"model": ErrorSchema},
    },
    dependencies=[Depends(HTTPBearer(auto_error=False))],
)
async def reorder_route(
    body: ReorderRouteCommand,
    handler: FromDishka[ReorderRouteCommandHandler],
) -> None:
    await handler.handle(body)


@router.patch(
    "/reverse",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
        status.HTTP_403_FORBIDDEN: {"model": ErrorSchema},
        status.HTTP_404_NOT_FOUND: {"model": ErrorSchema},
    },
    dependencies=[Depends(HTTPBearer(auto_error=False))],
)
async def reverse_route(
    body: ReverseRouteCommand,
    handler: FromDishka[ReverseRouteCommandHandler],
) -> None:
    await handler.handle(body)


@router.patch(
    "/orders/{order_id}/coordinates",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
        status.HTTP_403_FORBIDDEN: {"model": ErrorSchema},
        status.HTTP_404_NOT_FOUND: {"model": ErrorSchema},
    },
    dependencies=[Depends(HTTPBearer(auto_error=False))],
)
async def update_order_coordinates(
    order_id: OrderId,
    body: UpdateCoordinatesSchema,
    handler: FromDishka[UpdateOrderCoordinatesCommandHandler],
) -> None:
    await handler.handle(
        UpdateOrderCoordinatesCommand(
            order_id=order_id,
            latitude=body.latitude,
            longitude=body.longitude,
        )
    )


@router.get(
    "/shared/{route_plan_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorSchema},
    },
)
async def get_shared_route(
    route_plan_id: RoutePlanId,
    handler: FromDishka[GetSharedRouteQueryHandler],
) -> RouteReadModel:
    return await handler.handle(route_plan_id)
