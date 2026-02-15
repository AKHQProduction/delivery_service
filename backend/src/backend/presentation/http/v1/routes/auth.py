from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.security import HTTPBearer

from backend.application.commands.login_telegram import (
    LoginTelegramCommand,
    LoginTelegramCommandHandler,
)
from backend.application.commands.logout import LogoutCommandHandler
from backend.application.queries.get_me import GetMeQueryHandler, GetMeResponse
from backend.infrastructure.idp import IdentityProvider
from backend.presentation.http.v1.schemas.error import ErrorSchema

router = APIRouter(prefix="/auth", tags=["Auth"], route_class=DishkaRoute)


@router.post(
    "/telegram",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema}},
)
async def login_telegram(
    command: LoginTelegramCommand,
    handler: FromDishka[LoginTelegramCommandHandler],
    response: Response,
) -> None:
    session_id = await handler.handle(command)
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=604800,
    )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(
    request: Request,
    handler: FromDishka[LogoutCommandHandler],
    response: Response,
) -> None:
    session_id = request.cookies.get("session_id")
    if session_id:
        await handler.handle(session_id)
    response.delete_cookie(
        key="session_id",
        httponly=True,
        secure=True,
        samesite="lax",
    )


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    responses={status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema}},
    dependencies=[Depends(HTTPBearer(auto_error=False))],
)
async def get_me(handler: FromDishka[GetMeQueryHandler]) -> GetMeResponse:
    return await handler.handle()


@router.get(
    "/check",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(HTTPBearer(auto_error=False))],
)
async def check_session(idp: FromDishka[IdentityProvider]) -> dict:
    user_id = await idp.current_user_id()
    return {"user_id": str(user_id)}
