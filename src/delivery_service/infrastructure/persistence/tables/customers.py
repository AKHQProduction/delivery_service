import sqlalchemy as sa
from sqlalchemy import and_, join
from sqlalchemy.orm import column_property

from delivery_service.domain.customers.customer import Customer
from delivery_service.domain.customers.phone_number import PhoneBook
from delivery_service.domain.shared.vo.address import DeliveryAddress
from delivery_service.infrastructure.persistence.tables.base import (
    MAPPER_REGISTRY,
    value_object_to_json,
)
from delivery_service.infrastructure.persistence.tables.users import (
    USERS_TABLE,
)

CUSTOMERS_TABLE = sa.Table(
    "customers",
    MAPPER_REGISTRY.metadata,
    sa.Column(
        "user_id",
        sa.UUID,
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    ),
    sa.Column(
        "shop_id",
        sa.UUID,
        sa.ForeignKey("shops.id", ondelete="CASCADE"),
        nullable=False,
    ),
    sa.Column("contacts", value_object_to_json(PhoneBook), nullable=True),
    sa.Column(
        "delivery_address",
        value_object_to_json(DeliveryAddress),
        nullable=True,
    ),
    sa.Column(
        "created_at",
        sa.DateTime,
        default=sa.func.now(),
        server_default=sa.func.now(),
        nullable=False,
    ),
    sa.Column(
        "updated_at",
        sa.DateTime,
        default=sa.func.now(),
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
        server_onupdate=sa.func.now(),
        nullable=True,
    ),
    sa.UniqueConstraint(
        "user_id", "shop_id", name="uq_customers_user_id_shop_id"
    ),
)

MAPPER_REGISTRY.map_imperatively(
    Customer,
    join(
        USERS_TABLE,
        CUSTOMERS_TABLE,
        and_(USERS_TABLE.c.id == CUSTOMERS_TABLE.c.user_id),
    ),
    properties={
        "_entity_id": column_property(
            USERS_TABLE.c.id, CUSTOMERS_TABLE.c.user_id
        ),
        "_full_name": USERS_TABLE.c.full_name,
        "_shop_id": CUSTOMERS_TABLE.c.shop_id,
        "_contacts": CUSTOMERS_TABLE.c.contacts,
        "_delivery_address": CUSTOMERS_TABLE.c.delivery_address,
    },
    exclude_properties=[
        USERS_TABLE.c.created_at,
        USERS_TABLE.c.updated_at,
    ],
)
