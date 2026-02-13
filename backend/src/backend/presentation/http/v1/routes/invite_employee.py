from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer

from backend.application.usecases.invite_employee.generate_invite_link import (
    GenerateInviteLinkCommand,
    GenerateInviteLinkCommandHandler,
)
from backend.presentation.http.v1.schemas.error import ErrorSchema

router = APIRouter(prefix="/links", tags=["Links"], route_class=DishkaRoute)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
        status.HTTP_403_FORBIDDEN: {"model": ErrorSchema},
    },
    dependencies=[Depends(HTTPBearer(auto_error=False))],
)
async def create_invite_link(
    body: GenerateInviteLinkCommand,
    handler: FromDishka[GenerateInviteLinkCommandHandler],
) -> str:
    return await handler.handle(body)
