from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Body, Depends, status
from fastapi.security import HTTPBearer

from backend.application.commands.create_payment_method import (
    CreatePaymentMethodCommand,
    CreatePaymentMethodCommandHandler,
)
from backend.application.commands.delete_payment_method import (
    DeletePaymentMethodCommand,
    DeletePaymentMethodCommandHandler,
)
from backend.application.commands.edit_payment_method import (
    EditPaymentMethodCommand,
    EditPaymentMethodCommandHandler,
)
from backend.application.dto.gateways.payment_method_gateway import (
    PaymentMethodReadModel,
)
from backend.application.queries.get_payment_methods import (
    GetPaymentMethodsQueryHandler,
)
from backend.application.vars import PaymentMethodId
from backend.presentation.http.v1.schemas.error import ErrorSchema
from backend.presentation.http.v1.schemas.payment_method import (
    EditPaymentMethodSchema,
)

router = APIRouter(
    prefix="/payment-methods",
    tags=["Payment Methods"],
    route_class=DishkaRoute,
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
async def create_payment_method(
    body: Annotated[CreatePaymentMethodCommand, Body()],
    handler: FromDishka[CreatePaymentMethodCommandHandler],
) -> PaymentMethodId:
    return await handler.handle(body)


@router.patch(
    "/{payment_method_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
        status.HTTP_403_FORBIDDEN: {"model": ErrorSchema},
        status.HTTP_404_NOT_FOUND: {"model": ErrorSchema},
        status.HTTP_409_CONFLICT: {"model": ErrorSchema},
    },
    dependencies=[Depends(HTTPBearer(auto_error=False))],
)
async def update_payment_method(
    payment_method_id: PaymentMethodId,
    body: EditPaymentMethodSchema,
    handler: FromDishka[EditPaymentMethodCommandHandler],
) -> None:
    await handler.handle(
        EditPaymentMethodCommand(
            payment_method_id=payment_method_id,
            name=body.name,
        )
    )


@router.delete(
    "/{payment_method_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
        status.HTTP_403_FORBIDDEN: {"model": ErrorSchema},
        status.HTTP_404_NOT_FOUND: {"model": ErrorSchema},
    },
    dependencies=[Depends(HTTPBearer(auto_error=False))],
)
async def delete_payment_method(
    payment_method_id: PaymentMethodId,
    handler: FromDishka[DeletePaymentMethodCommandHandler],
) -> None:
    await handler.handle(
        DeletePaymentMethodCommand(payment_method_id=payment_method_id)
    )


@router.get(
    "/all",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
    },
    dependencies=[Depends(HTTPBearer(auto_error=False))],
)
async def get_all_payment_methods(
    handler: FromDishka[GetPaymentMethodsQueryHandler],
) -> list[PaymentMethodReadModel]:
    return await handler.handle()
