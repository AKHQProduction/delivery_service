from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Body, Depends, status
from fastapi.security import HTTPBearer

from backend.application.commands.create_time_slot import (
    CreateTimeSlotCommand,
    CreateTimeSlotCommandHandler,
)
from backend.application.commands.delete_time_slot import (
    DeleteTimeSlotCommand,
    DeleteTimeSlotCommandHandler,
)
from backend.application.commands.edit_time_slot import (
    EditTimeSlotCommand,
    EditTimeSlotCommandHandler,
)
from backend.application.dto.gateways.time_slot_gateway import (
    TimeSlotReadModel,
)
from backend.application.queries.get_time_slots import GetTimeSlotsQueryHandler
from backend.application.vars import TimeSlotId
from backend.presentation.http.v1.schemas.error import ErrorSchema
from backend.presentation.http.v1.schemas.time_slot import EditTimeSlotSchema

router = APIRouter(
    prefix="/time-slots", tags=["Time Slots"], route_class=DishkaRoute
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
        status.HTTP_403_FORBIDDEN: {"model": ErrorSchema},
        status.HTTP_409_CONFLICT: {"model": ErrorSchema},
    },
    dependencies=[Depends(HTTPBearer(auto_error=False))],
)
async def create_time_slot(
    body: Annotated[CreateTimeSlotCommand, Body()],
    handler: FromDishka[CreateTimeSlotCommandHandler],
) -> TimeSlotId:
    return await handler.handle(body)


@router.patch(
    "/{time_slot_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
        status.HTTP_403_FORBIDDEN: {"model": ErrorSchema},
        status.HTTP_404_NOT_FOUND: {"model": ErrorSchema},
        status.HTTP_409_CONFLICT: {"model": ErrorSchema},
    },
    dependencies=[Depends(HTTPBearer(auto_error=False))],
)
async def update_time_slot(
    time_slot_id: TimeSlotId,
    body: EditTimeSlotSchema,
    handler: FromDishka[EditTimeSlotCommandHandler],
) -> None:
    await handler.handle(
        EditTimeSlotCommand(
            time_slot_id=time_slot_id,
            start_time=body.start_time,
            end_time=body.end_time,
            label=body.label,
        )
    )


@router.delete(
    "/{time_slot_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
        status.HTTP_403_FORBIDDEN: {"model": ErrorSchema},
        status.HTTP_404_NOT_FOUND: {"model": ErrorSchema},
    },
    dependencies=[Depends(HTTPBearer(auto_error=False))],
)
async def delete_time_slot(
    time_slot_id: TimeSlotId,
    handler: FromDishka[DeleteTimeSlotCommandHandler],
) -> None:
    await handler.handle(DeleteTimeSlotCommand(time_slot_id=time_slot_id))


@router.get(
    "/all",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
    },
    dependencies=[Depends(HTTPBearer(auto_error=False))],
)
async def get_all_time_slots(
    handler: FromDishka[GetTimeSlotsQueryHandler],
) -> list[TimeSlotReadModel]:
    return await handler.handle()
