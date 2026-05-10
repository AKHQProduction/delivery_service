from dataclasses import dataclass
from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Body, Depends, Query, status
from fastapi.security import HTTPBearer

from backend.application.commands.create_recurring_order import (
    CreateRecurringOrderCommand,
    CreateRecurringOrderCommandHandler,
    RecurringOrderProductInput,
)
from backend.application.commands.delete_recurring_order import (
    DeleteRecurringOrderCommand,
    DeleteRecurringOrderCommandHandler,
)
from backend.application.commands.pause_recurring_order import (
    PauseRecurringOrderCommand,
    PauseRecurringOrderCommandHandler,
)
from backend.application.commands.resume_recurring_order import (
    ResumeRecurringOrderCommand,
    ResumeRecurringOrderCommandHandler,
)
from backend.application.commands.run_recurring_order import (
    RunRecurringOrderCommand,
    RunRecurringOrderCommandHandler,
    RunRecurringOrderResult,
)
from backend.application.commands.update_recurring_order import (
    UpdateRecurringOrderCommand,
    UpdateRecurringOrderCommandHandler,
)
from backend.application.dto.gateways.recurring_order_gateway import (
    RecurringOrderDetailReadModel,
    RecurringOrderReadModel,
)
from backend.application.queries.get_recurring_order import (
    GetRecurringOrderQuery,
    GetRecurringOrderQueryHandler,
)
from backend.application.queries.get_recurring_orders import (
    GetRecurringOrdersQuery,
    GetRecurringOrdersQueryHandler,
)
from backend.application.vars import (
    AddressId,
    ClientId,
    PhoneId,
    RecurringOrderId,
    RecurringOrderStatus,
    ScheduleType,
    TimeSlotId,
)
from backend.presentation.http.v1.schemas.error import ErrorSchema


@dataclass(frozen=True)
class RunRecurringOrderRequest:
    include_today: bool = False
    activate: bool = False


@dataclass(frozen=True)
class UpdateRecurringOrderRequest:
    address_id: AddressId
    phone_id: PhoneId
    time_slot_id: TimeSlotId
    items: list[RecurringOrderProductInput]
    payment_method: str
    schedule_type: ScheduleType
    weekdays: list[int] | None = None
    month_days: list[int] | None = None
    comment: str | None = None


router = APIRouter(
    prefix="/recurring-orders",
    tags=["Recurring Orders"],
    route_class=DishkaRoute,
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
        status.HTTP_403_FORBIDDEN: {"model": ErrorSchema},
        status.HTTP_404_NOT_FOUND: {"model": ErrorSchema},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ErrorSchema},
    },
    dependencies=[Depends(HTTPBearer(auto_error=False))],
)
async def create_recurring_order(
    body: Annotated[CreateRecurringOrderCommand, Body()],
    handler: FromDishka[CreateRecurringOrderCommandHandler],
) -> RecurringOrderId:
    return await handler.handle(body)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    responses={status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema}},
    dependencies=[Depends(HTTPBearer(auto_error=False))],
)
async def get_recurring_orders(
    handler: FromDishka[GetRecurringOrdersQueryHandler],
    client_id: ClientId | None = None,
    client_name: str | None = None,
    status_filter: Annotated[
        RecurringOrderStatus | None, Query(alias="status")
    ] = None,
    schedule_type: ScheduleType | None = None,
    weekday: int | None = None,
    month_day: int | None = None,
) -> list[RecurringOrderReadModel]:
    return await handler.handle(
        GetRecurringOrdersQuery(
            client_id=client_id,
            client_name=client_name,
            status=status_filter,
            schedule_type=schedule_type,
            weekday=weekday,
            month_day=month_day,
        )
    )


@router.get(
    "/{recurring_order_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
        status.HTTP_404_NOT_FOUND: {"model": ErrorSchema},
    },
    dependencies=[Depends(HTTPBearer(auto_error=False))],
)
async def get_recurring_order(
    recurring_order_id: RecurringOrderId,
    handler: FromDishka[GetRecurringOrderQueryHandler],
) -> RecurringOrderDetailReadModel:
    return await handler.handle(GetRecurringOrderQuery(recurring_order_id))


@router.patch(
    "/{recurring_order_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
        status.HTTP_403_FORBIDDEN: {"model": ErrorSchema},
        status.HTTP_404_NOT_FOUND: {"model": ErrorSchema},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ErrorSchema},
    },
    dependencies=[Depends(HTTPBearer(auto_error=False))],
)
async def update_recurring_order(
    recurring_order_id: RecurringOrderId,
    body: Annotated[UpdateRecurringOrderRequest, Body()],
    handler: FromDishka[UpdateRecurringOrderCommandHandler],
    rebuild_future_orders: bool = False,
) -> None:
    await handler.handle(
        UpdateRecurringOrderCommand(
            recurring_order_id=recurring_order_id,
            address_id=body.address_id,
            phone_id=body.phone_id,
            time_slot_id=body.time_slot_id,
            items=body.items,
            payment_method=body.payment_method,
            schedule_type=body.schedule_type,
            weekdays=body.weekdays,
            month_days=body.month_days,
            comment=body.comment,
            rebuild_future_orders=rebuild_future_orders,
        )
    )


@router.post(
    "/{recurring_order_id}/pause",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
        status.HTTP_404_NOT_FOUND: {"model": ErrorSchema},
    },
    dependencies=[Depends(HTTPBearer(auto_error=False))],
)
async def pause_recurring_order(
    recurring_order_id: RecurringOrderId,
    handler: FromDishka[PauseRecurringOrderCommandHandler],
    cancel_future_orders: bool = False,
) -> None:
    await handler.handle(
        PauseRecurringOrderCommand(
            recurring_order_id,
            cancel_future_orders=cancel_future_orders,
        )
    )


@router.post(
    "/{recurring_order_id}/resume",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
        status.HTTP_404_NOT_FOUND: {"model": ErrorSchema},
    },
    dependencies=[Depends(HTTPBearer(auto_error=False))],
)
async def resume_recurring_order(
    recurring_order_id: RecurringOrderId,
    handler: FromDishka[ResumeRecurringOrderCommandHandler],
) -> None:
    await handler.handle(ResumeRecurringOrderCommand(recurring_order_id))


@router.post(
    "/{recurring_order_id}/run",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
        status.HTTP_404_NOT_FOUND: {"model": ErrorSchema},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ErrorSchema},
    },
    dependencies=[Depends(HTTPBearer(auto_error=False))],
)
async def run_recurring_order(
    recurring_order_id: RecurringOrderId,
    body: Annotated[RunRecurringOrderRequest, Body()],
    handler: FromDishka[RunRecurringOrderCommandHandler],
) -> RunRecurringOrderResult:
    return await handler.handle(
        RunRecurringOrderCommand(
            recurring_order_id=recurring_order_id,
            include_today=body.include_today,
            activate=body.activate,
        )
    )


@router.delete(
    "/{recurring_order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
        status.HTTP_404_NOT_FOUND: {"model": ErrorSchema},
    },
    dependencies=[Depends(HTTPBearer(auto_error=False))],
)
async def delete_recurring_order(
    recurring_order_id: RecurringOrderId,
    handler: FromDishka[DeleteRecurringOrderCommandHandler],
    delete_future_orders: bool = False,
) -> None:
    await handler.handle(
        DeleteRecurringOrderCommand(
            recurring_order_id,
            delete_future_orders=delete_future_orders,
        )
    )
