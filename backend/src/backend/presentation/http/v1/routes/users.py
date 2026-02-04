from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer

from backend.application.dto.idp import CurrentUserDTO
from backend.infrastructure.idp import TelegramIdentityProvider
from backend.presentation.http.v1.schemas.error import ErrorSchema

router = APIRouter(prefix="/users", tags=["User"], route_class=DishkaRoute)


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    responses={status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema}},
    dependencies=[Depends(HTTPBearer())],
)
async def get_me(idp: FromDishka[TelegramIdentityProvider]) -> CurrentUserDTO:
    return await idp.current_user()
