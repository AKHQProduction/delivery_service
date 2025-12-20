from datetime import UTC, date, datetime, timedelta
from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Body, Depends, status
from fastapi.openapi.models import Example
from fastapi.responses import Response
from fastapi.security import HTTPBearer

from backend.application.commands.create_order import (
    CreateOrderCommand,
    CreateOrderCommandHandler,
)
from backend.application.commands.delete_order import (
    DeleteOrderCommand,
    DeleteOrderCommandHandler,
)
from backend.application.commands.edit_order import (
    OrderItem,
    UpdateOrderCommand,
    UpdateOrderCommandHandler,
)
from backend.application.interfaces.gateways import Pagination
from backend.application.interfaces.gateways.order_gateway import (
    OrderReadModel,
)
from backend.application.queries.export_orders_pdf import (
    ExportOrdersPDFQuery,
    ExportOrdersPDFQueryHandler,
)
from backend.application.queries.get_order import GetOrderQueryHandler
from backend.application.queries.get_orders import (
    GetOrdersQuery,
    GetOrdersQueryHandler,
)
from backend.application.vars import OrderId, TimePreference
from backend.presentation.http.v1.schemas.error import ErrorSchema
from backend.presentation.http.v1.schemas.order import UpdateOrderSchema

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


@router.patch(
    "/{order_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
        status.HTTP_403_FORBIDDEN: {"model": ErrorSchema},
        status.HTTP_404_NOT_FOUND: {"model": ErrorSchema},
    },
    dependencies=[Depends(HTTPBearer())],
)
async def update_order(
    order_id: OrderId,
    body: Annotated[
        UpdateOrderSchema,
        Body(
            openapi_examples={
                "change_delivery_date": Example(
                    description="Change delivery date and time preference",
                    value={
                        "delivery_date": (
                            datetime.now(UTC).date() + timedelta(days=2)
                        ).isoformat(),
                        "time_preference": TimePreference.SECOND_HALF,
                    },
                ),
                "change_client": Example(
                    description="Change client with new phone and address",
                    value={
                        "client_id": "650e8400-e29b-41d4-a716-446655440000",
                        "phone_id": 1,
                        "address_id": 2,
                    },
                ),
                "change_phone_only": Example(
                    description="Change delivery phone only",
                    value={
                        "phone_id": 2,
                    },
                ),
                "change_address_only": Example(
                    description="Change delivery address only",
                    value={
                        "address_id": 3,
                    },
                ),
                "update_item_quantity": Example(
                    description=(
                        "Update quantity of existing item. "
                        "Pass id to keep the item, change quantity. "
                        "No need to pass product_id for existing items. "
                        "If order has items [id=1, id=2], this keeps both "
                        "but changes quantity of item 1 to 10."
                    ),
                    value={
                        "items": [
                            {"id": 1, "quantity": 10},
                            {"id": 2, "quantity": 2},
                        ],
                    },
                ),
                "add_new_item": Example(
                    description=(
                        "Add new item to order. "
                        "Keep existing items (pass their ids), "
                        "add new item with product_id but without id. "
                        "If order has [id=1], this keeps it and adds new."
                    ),
                    value={
                        "items": [
                            {"id": 1, "quantity": 1},
                            {
                                "product_id": (
                                    "850e8400-e29b-41d4-a716-446655440000"
                                ),
                                "quantity": 3,
                            },
                        ],
                    },
                ),
                "delete_item": Example(
                    description=(
                        "Delete item from order. "
                        "Simply don't include it in the list. "
                        "If order has [id=1, id=2, id=3], "
                        "this removes id=2 and id=3."
                    ),
                    value={
                        "items": [
                            {"id": 1, "quantity": 1},
                        ],
                    },
                ),
                "replace_all_items": Example(
                    description=(
                        "Replace all items with completely new list. "
                        "Don't pass any ids - all old items will be deleted, "
                        "new items will be created."
                    ),
                    value={
                        "items": [
                            {
                                "product_id": (
                                    "750e8400-e29b-41d4-a716-446655440000"
                                ),
                                "quantity": 2,
                            },
                            {
                                "product_id": (
                                    "850e8400-e29b-41d4-a716-446655440000"
                                ),
                                "quantity": 1,
                            },
                        ],
                    },
                ),
                "update_comment": Example(
                    description="Update order comment (set new value)",
                    value={
                        "comment": "Новий коментар до замовлення",
                    },
                ),
                "clear_comment": Example(
                    description="Clear order comment (set to empty)",
                    value={
                        "comment": "EMPTY",
                    },
                ),
                "full_update": Example(
                    description="Full order update with all fields",
                    value={
                        "client_id": "650e8400-e29b-41d4-a716-446655440000",
                        "delivery_date": (
                            datetime.now(UTC).date() + timedelta(days=3)
                        ).isoformat(),
                        "time_preference": TimePreference.FIRST_HALF,
                        "phone_id": 1,
                        "address_id": 2,
                        "comment": "Терміново",
                        "items": [
                            {"id": 1, "quantity": 10},
                            {
                                "product_id": (
                                    "750e8400-e29b-41d4-a716-446655440000"
                                ),
                                "quantity": 1,
                            },
                        ],
                    },
                ),
            }
        ),
    ],
    handler: FromDishka[UpdateOrderCommandHandler],
) -> None:
    items = (
        [
            OrderItem(
                product_id=item.product_id,
                quantity=item.quantity,
                id=item.id,
            )
            for item in body.items
        ]
        if body.items
        else None
    )
    command = UpdateOrderCommand(
        order_id=order_id,
        client_id=body.client_id,
        delivery_date=body.delivery_date,
        time_preference=body.time_preference,
        address_id=body.address_id,
        phone_id=body.phone_id,
        comment=body.comment,
        items=items,
    )
    await handler.handle(command)


@router.delete(
    "/{order_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
        status.HTTP_403_FORBIDDEN: {"model": ErrorSchema},
    },
    dependencies=[Depends(HTTPBearer())],
)
async def delete_order(
    order_id: OrderId, handler: FromDishka[DeleteOrderCommandHandler]
) -> None:
    await handler.handle(DeleteOrderCommand(order_id=order_id))


@router.get(
    "/all",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
    },
    dependencies=[Depends(HTTPBearer())],
)
async def get_all_orders(
    handler: FromDishka[GetOrdersQueryHandler],
    delivery_date: date | None = None,
    time_preference: TimePreference | None = None,
    client_name: str | None = None,
    custom_id: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[OrderReadModel]:
    return await handler.handle(
        GetOrdersQuery(
            delivery_date=delivery_date,
            time_preference=time_preference,
            client_name=client_name,
            custom_id=custom_id,
            pagination=Pagination(limit=limit, offset=offset),
        )
    )


@router.get(
    "/export/pdf",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
        status.HTTP_403_FORBIDDEN: {"model": ErrorSchema},
        status.HTTP_404_NOT_FOUND: {"model": ErrorSchema},
    },
    dependencies=[Depends(HTTPBearer())],
)
async def export_orders_pdf(
    delivery_date: date,
    handler: FromDishka[ExportOrdersPDFQueryHandler],
) -> Response:
    query = ExportOrdersPDFQuery(delivery_date=delivery_date)
    pdf_bytes = await handler.handle(query)
    filename = f"orders_{delivery_date.isoformat()}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get(
    "/{order_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
        status.HTTP_404_NOT_FOUND: {"model": ErrorSchema},
    },
    dependencies=[Depends(HTTPBearer())],
)
async def get_order(
    order_id: OrderId, handler: FromDishka[GetOrderQueryHandler]
) -> OrderReadModel:
    return await handler.handle(order_id=order_id)
