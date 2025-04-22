import sqlalchemy as sa
from sqlalchemy import and_, join
from sqlalchemy.orm import column_property, foreign, relationship

from delivery_service.domain.addresses.address import Address
from delivery_service.domain.customers.customer import Customer
from delivery_service.domain.customers.phone_number import PhoneBook
from delivery_service.domain.shared.vo.address import Coordinates
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

ADDRESSES_TABLE = sa.Table(
    "addresses",
    MAPPER_REGISTRY.metadata,
    sa.Column("id", sa.UUID, primary_key=True),
    sa.Column(
        "user_id",
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    ),
    sa.Column("city", sa.String, nullable=False),
    sa.Column("street", sa.String, nullable=False),
    sa.Column("house_number", sa.String, nullable=False),
    sa.Column("apartment_number", sa.String, nullable=True),
    sa.Column("floor", sa.Integer, nullable=True),
    sa.Column("intercom_code", sa.String, nullable=True),
    sa.Column("coordinates", value_object_to_json(Coordinates), nullable=True),
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
        "user_id", "city", "street", "house_number", name="uq_user_address"
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
        "_delivery_addresses": relationship(
            Address,
            primaryjoin=and_(
                CUSTOMERS_TABLE.c.user_id == foreign(ADDRESSES_TABLE.c.user_id)
            ),
            foreign_keys=[ADDRESSES_TABLE.c.user_id],
            back_populates="_customer",
            cascade="all, delete-orphan",
            lazy="selectin",
        ),
    },
    exclude_properties=[
        USERS_TABLE.c.created_at,
        USERS_TABLE.c.updated_at,
    ],
)

MAPPER_REGISTRY.map_imperatively(
    Address,
    ADDRESSES_TABLE,
    properties={
        "_entity_id": ADDRESSES_TABLE.c.id,
        "_client_id": ADDRESSES_TABLE.c.user_id,
        "_city": ADDRESSES_TABLE.c.city,
        "_street": ADDRESSES_TABLE.c.street,
        "_house_number": ADDRESSES_TABLE.c.house_number,
        "_apartment_number": ADDRESSES_TABLE.c.apartment_number,
        "_floor": ADDRESSES_TABLE.c.floor,
        "_intercom_code": ADDRESSES_TABLE.c.intercom_code,
        "_coordinates": ADDRESSES_TABLE.c.coordinates,
        "_customer": relationship(
            Customer,
            primaryjoin=and_(
                foreign(ADDRESSES_TABLE.c.user_id) == CUSTOMERS_TABLE.c.user_id
            ),
            foreign_keys=[ADDRESSES_TABLE.c.user_id],
            back_populates="_delivery_addresses",
        ),
    },
)
