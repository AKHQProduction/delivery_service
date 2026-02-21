from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Body, Depends, HTTPException, UploadFile, status
from fastapi.openapi.models import Example
from fastapi.responses import Response
from fastapi.security import HTTPBearer

from backend.application.commands.create_client import (
    CreateClientCommand,
    CreateClientCommandHandler,
)
from backend.application.commands.delete_client import (
    DeleteClientCommand,
    DeleteClientCommandHandler,
)
from backend.application.commands.edit_client import (
    Address,
    EditClientCommand,
    EditClientCommandHandler,
    Phone,
)
from backend.application.commands.import_clients import (
    ImportClientsCommand,
    ImportClientsCommandHandler,
    ImportClientsResult,
)
from backend.application.dto.coordinates import CoordinatesDTO
from backend.application.dto.gateways import Pagination, SortOrder
from backend.application.dto.gateways.client_gateway import (
    ClientReadModel,
)
from backend.application.queries.get_client import GetClientQueryHandler
from backend.application.queries.get_clients import (
    GetClientsQuery,
    GetClientsQueryHandler,
)
from backend.application.vars import AddressId, ClientId, DistrictId, PhoneId
from backend.infrastructure.persistence.gateways import RedisFileStorage
from backend.presentation.http.v1.schemas.client import EditClientSchema
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
        status.HTTP_409_CONFLICT: {"model": ErrorSchema},
    },
    dependencies=[Depends(HTTPBearer(auto_error=False))],
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
                                "apartment": "5",
                                "entrance": "1",
                                "floor": "2",
                                "intercom": "5",
                                "comment": "Біля метро",
                            },
                            {
                                "street": "Шевченка",
                                "house": "25",
                                "apartment": "12",
                                "entrance": "2",
                                "floor": "3",
                            },
                        ],
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
                                "comment": "Приватний будинок, ворота сині",
                            }
                        ],
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
                                "apartment": "10",
                                "entrance": "1",
                                "floor": "3",
                                "intercom": "10",
                            },
                            {
                                "street": "Садова",
                                "house": "22Б",
                                "comment": "Будинок з зеленим дахом",
                            },
                        ],
                    },
                ),
                "confirm_duplicate_phones": Example(
                    description=(
                        "Create client with confirmed duplicate phones"
                    ),
                    value={
                        "full_name": "Олена Олійник",
                        "phones": [
                            {"number": "+380501234567"},
                        ],
                        "addresses": [
                            {
                                "street": "Хрещатик",
                                "house": "10",
                            },
                        ],
                        "confirm_duplicate_phones": True,
                    },
                ),
            }
        ),
    ],
    handler: FromDishka[CreateClientCommandHandler],
) -> ClientId:
    return await handler.handle(body)


@router.patch(
    "/{client_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
        status.HTTP_403_FORBIDDEN: {"model": ErrorSchema},
        status.HTTP_404_NOT_FOUND: {"model": ErrorSchema},
        status.HTTP_409_CONFLICT: {"model": ErrorSchema},
    },
    dependencies=[Depends(HTTPBearer(auto_error=False))],
)
async def update_client(
    client_id: ClientId,
    body: Annotated[
        EditClientSchema,
        Body(
            openapi_examples={
                "full_name": Example(
                    description="Update only client's full name",
                    value={"full_name": "Оновлене Ім'я"},
                ),
                "phones": Example(
                    description="Update existing phones and add new ones",
                    value={
                        "phones": [
                            {
                                "number": "+380509999999",
                                "is_primary": True,
                                "id": 1,
                            },
                            {
                                "number": "+380508888888",
                                "is_primary": False,
                            },
                        ]
                    },
                ),
                "addresses": Example(
                    description="Update existing addresses and add new ones",
                    value={
                        "addresses": [
                            {
                                "street": "Оновлена вулиця",
                                "house": "100",
                                "apartment": "50",
                                "entrance": "2",
                                "floor": "10",
                                "intercom": "50",
                                "comment": "Біля парку",
                                "is_primary": True,
                                "id": 5,
                            }
                        ]
                    },
                ),
                "all_fields": Example(
                    description="Update all fields at once",
                    value={
                        "full_name": "Повністю Оновлене Ім'я",
                        "phones": [
                            {
                                "number": "+380501234567",
                                "is_primary": True,
                                "id": 2,
                            }
                        ],
                        "addresses": [
                            {
                                "street": "Повністю нова адреса",
                                "house": "1",
                                "comment": "Новий будинок",
                                "is_primary": True,
                            }
                        ],
                    },
                ),
                "clear_phones": Example(
                    description="Clear all phones (empty array)",
                    value={"phones": []},
                ),
                "confirm_duplicate_phones": Example(
                    description=("Update phones with confirmed duplicates"),
                    value={
                        "phones": [
                            {
                                "number": "+380501234567",
                                "is_primary": True,
                            },
                        ],
                        "confirm_duplicate_phones": True,
                    },
                ),
            }
        ),
    ],
    handler: FromDishka[EditClientCommandHandler],
) -> None:
    await handler.handle(
        EditClientCommand(
            client_id=client_id,
            full_name=body.full_name,
            confirm_duplicate_phones=body.confirm_duplicate_phones,
            phones=[
                Phone(
                    number=phone.number,
                    is_primary=phone.is_primary,
                    id=PhoneId(phone.id) if phone.id is not None else None,
                )
                for phone in body.phones
            ]
            if body.phones is not None
            else None,
            addresses=[
                Address(
                    street=address.street,
                    house=address.house,
                    apartment=address.apartment,
                    entrance=address.entrance,
                    floor=address.floor,
                    intercom=address.intercom,
                    comment=address.comment,
                    coordinates=CoordinatesDTO(
                        latitude=address.coordinates.latitude,
                        longitude=address.coordinates.longitude,
                    )
                    if address.coordinates is not None
                    else None,
                    is_primary=address.is_primary,
                    id=AddressId(address.id)
                    if address.id is not None
                    else None,
                    district_id=DistrictId(address.district_id)
                    if address.district_id is not None
                    else None,
                )
                for address in body.addresses
            ]
            if body.addresses is not None
            else None,
        )
    )


@router.post(
    "/import",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
        status.HTTP_403_FORBIDDEN: {"model": ErrorSchema},
    },
    dependencies=[Depends(HTTPBearer(auto_error=False))],
)
async def import_clients(
    file: UploadFile,
    handler: FromDishka[ImportClientsCommandHandler],
) -> ImportClientsResult:
    if not file.filename or not file.filename.endswith(".xlsx"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Only .xlsx files are supported",
        )
    file_bytes = await file.read()
    return await handler.handle(ImportClientsCommand(file_bytes=file_bytes))


@router.get(
    "/export/errors/{file_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorSchema},
    },
)
async def download_import_errors(
    file_id: str,
    file_storage: FromDishka[RedisFileStorage],
) -> Response:
    result = await file_storage.get(file_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found or expired",
        )
    content, filename = result
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get(
    "/all",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
    },
    dependencies=[Depends(HTTPBearer(auto_error=False))],
)
async def get_all_clients(
    handler: FromDishka[GetClientsQueryHandler],
    full_name: str | None = None,
    phone: str | None = None,
    limit: int = 100,
    offset: int = 0,
    order: SortOrder = SortOrder.ASC,
) -> list[ClientReadModel]:
    return await handler.handle(
        GetClientsQuery(
            full_name=full_name,
            phone=phone,
            pagination=Pagination(limit=limit, offset=offset, order=order),
        )
    )


@router.get(
    "/{client_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
        status.HTTP_404_NOT_FOUND: {"model": ErrorSchema},
    },
    dependencies=[Depends(HTTPBearer(auto_error=False))],
)
async def get_client(
    client_id: ClientId, handler: FromDishka[GetClientQueryHandler]
) -> ClientReadModel:
    return await handler.handle(client_id=client_id)


@router.delete(
    "/{client_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
        status.HTTP_403_FORBIDDEN: {"model": ErrorSchema},
        status.HTTP_404_NOT_FOUND: {"model": ErrorSchema},
    },
    dependencies=[Depends(HTTPBearer(auto_error=False))],
)
async def delete_client(
    client_id: ClientId, handler: FromDishka[DeleteClientCommandHandler]
) -> None:
    await handler.handle(DeleteClientCommand(client_id=client_id))
