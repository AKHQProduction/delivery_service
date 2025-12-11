from datetime import UTC, datetime, timedelta
from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Body, Depends, status
from fastapi.openapi.models import Example
from fastapi.security import HTTPBearer

from backend.application.commands.create_order import (
    CreateOrderCommand,
    CreateOrderCommandHandler,
)
from backend.application.vars import OrderId, TimePreference
from backend.presentation.http.v1.schemas.error import ErrorSchema

router = APIRouter(prefix="/orders", tags=["Orders"], route_class=DishkaRoute)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
        status.HTTP_403_FORBIDDEN: {"model": ErrorSchema},
        status.HTTP_404_NOT_FOUND: {"model": ErrorSchema},
    },
    dependencies=[Depends(HTTPBearer())],
)
async def create_new_order(
    body: Annotated[
        CreateOrderCommand,
        Body(
            openapi_examples={
                "single_product": Example(
                    description="Create order with single product",
                    value={
                        "client_id": "550e8400-e29b-41d4-a716-446655440000",
                        "delivery_date": (
                            datetime.now(UTC).date() + timedelta(days=1)
                        ).isoformat(),
                        "time_preference": TimePreference.FIRST_HALF,
                        "address_id": 1,
                        "phone_id": 1,
                        "products": [
                            {
                                "product_id": (
                                    "650e8400-e29b-41d4-a716-446655440000"
                                ),
                                "quantity": 2,
                            }
                        ],
                        "comment": (
                            "Доставити до 12:00, передзвоніть за 30 хвилин"
                        ),
                    },
                ),
                "multiple_products": Example(
                    description="Create order with multiple products",
                    value={
                        "client_id": "550e8400-e29b-41d4-a716-446655440000",
                        "delivery_date": (
                            datetime.now(UTC).date() + timedelta(days=2)
                        ).isoformat(),
                        "time_preference": TimePreference.SECOND_HALF,
                        "address_id": 2,
                        "phone_id": 1,
                        "products": [
                            {
                                "product_id": (
                                    "650e8400-e29b-41d4-a716-446655440000"
                                ),
                                "quantity": 3,
                            },
                            {
                                "product_id": (
                                    "750e8400-e29b-41d4-a716-446655440000"
                                ),
                                "quantity": 1,
                            },
                            {
                                "product_id": (
                                    "850e8400-e29b-41d4-a716-446655440000"
                                ),
                                "quantity": 50,
                            },
                        ],
                        "comment": "Доставка після 14:00, домофон не працює",
                    },
                ),
                "no_comment": Example(
                    description="Create order without comment",
                    value={
                        "client_id": "550e8400-e29b-41d4-a716-446655440000",
                        "delivery_date": (
                            datetime.now(UTC).date() + timedelta(days=1)
                        ).isoformat(),
                        "time_preference": TimePreference.FIRST_HALF,
                        "address_id": 1,
                        "phone_id": 2,
                        "products": [
                            {
                                "product_id": (
                                    "650e8400-e29b-41d4-a716-446655440000"
                                ),
                                "quantity": 1,
                            }
                        ],
                    },
                ),
            }
        ),
    ],
    handler: FromDishka[CreateOrderCommandHandler],
) -> OrderId:
    return await handler.handle(body)
