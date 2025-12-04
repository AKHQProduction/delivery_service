from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Body, Depends, status
from fastapi.openapi.models import Example
from fastapi.security import HTTPBearer

from backend.application.commands.create_client import (
    CreateClientCommand,
    CreateClientCommandHandler,
)
from backend.application.vars import AddressType, ClientId
from backend.presentation.http.v1.schemas.error import ErrorSchema

router = APIRouter(
    prefix="/clients", tags=["Clients"], route_class=DishkaRoute
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
        status.HTTP_403_FORBIDDEN: {"model": ErrorSchema},
    },
    dependencies=[Depends(HTTPBearer())],
)
async def create_new_client(
    body: Annotated[
        CreateClientCommand,
        Body(
            openapi_examples={
                "apartment": Example(
                    description="Create client with apartment address",
                    value={
                        "full_name": "Іван Іванов",
                        "phones": [
                            {"number": "+380501234567"},
                            {"number": "+380507654321"},
                        ],
                        "addresses": [
                            {
                                "street": "Хрещатик",
                                "house": "10",
                                "address_type": AddressType.APARTMENT,
                                "apartment": "5",
                                "entrance": "1",
                                "floor": "2",
                                "intercom": "5",
                            },
                            {
                                "street": "Шевченка",
                                "house": "25",
                                "address_type": AddressType.APARTMENT,
                                "apartment": "12",
                                "entrance": "2",
                                "floor": "3",
                            },
                        ],
                        "custom_id": None,
                    },
                ),
                "private_house": Example(
                    description="Create client with private house address",
                    value={
                        "full_name": "Петро Петренко",
                        "phones": [
                            {"number": "+380931234567"},
                        ],
                        "addresses": [
                            {
                                "street": "Заміська",
                                "house": "15А",
                                "address_type": AddressType.PRIVATE_HOUSE,
                                "apartment": None,
                                "entrance": None,
                                "floor": None,
                                "intercom": None,
                            }
                        ],
                        "custom_id": "HOUSE-001",
                    },
                ),
                "multiple_addresses": Example(
                    description=(
                        "Client with multiple addresses "
                        "(apartment and private house)"
                    ),
                    value={
                        "full_name": "Марія Марченко",
                        "phones": [
                            {"number": "+380671234567"},
                            {"number": "+380631234567"},
                        ],
                        "addresses": [
                            {
                                "street": "Грушевського",
                                "house": "5",
                                "address_type": AddressType.APARTMENT,
                                "apartment": "10",
                                "entrance": "1",
                                "floor": "3",
                                "intercom": "10",
                            },
                            {
                                "street": "Садова",
                                "house": "22Б",
                                "address_type": AddressType.PRIVATE_HOUSE,
                            },
                        ],
                    },
                ),
            }
        ),
    ],
    handler: FromDishka[CreateClientCommandHandler],
) -> ClientId:
    return await handler.handle(body)
