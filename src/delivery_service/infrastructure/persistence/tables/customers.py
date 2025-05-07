import sqlalchemy as sa
from sqlalchemy import and_
from sqlalchemy.orm import foreign, relationship

from delivery_service.domain.addresses.address import Address
from delivery_service.domain.customers.customer import Customer
from delivery_service.domain.customers.phone_number import (
    PhoneNumber,
)
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
    sa.Column("id", sa.UUID, primary_key=True),
    sa.Column("name", sa.String, nullable=False),
    sa.Column(
        "user_id",
        sa.UUID,
        sa.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    ),
    sa.Column(
        "shop_id",
        sa.UUID,
        sa.ForeignKey("shops.id", ondelete="CASCADE"),
        nullable=False,
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
)

ADDRESSES_TABLE = sa.Table(
    "addresses",
    MAPPER_REGISTRY.metadata,
    sa.Column("id", sa.UUID, primary_key=True),
    sa.Column(
        "customer_id",
        sa.ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
    ),
    sa.Column("shop_id", sa.ForeignKey("shops.id"), onupdate="CASCADE"),
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
        "shop_id", "city", "street", "house_number", name="uq_user_address"
    ),
)

PHONE_NUMBER_TABLE = sa.Table(
    "phone_numbers",
    MAPPER_REGISTRY.metadata,
    sa.Column("id", sa.UUID, primary_key=True),
    sa.Column(
        "customer_id",
        sa.ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
    ),
    sa.Column(
        "shop_id",
        sa.UUID,
        sa.ForeignKey("shops.id", ondelete="CASCADE"),
        nullable=False,
    ),
    sa.Column("number", sa.String, nullable=False),
    sa.Column("is_primary", sa.Boolean, nullable=False, default=False),
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
)

MAPPER_REGISTRY.map_imperatively(
    Customer,
    CUSTOMERS_TABLE,
    properties={
        "_entity_id": CUSTOMERS_TABLE.c.id,
        "_name": CUSTOMERS_TABLE.c.name,
        "_user_id": CUSTOMERS_TABLE.c.user_id,
        "_contacts": relationship(
            PhoneNumber,
            primaryjoin=and_(
                CUSTOMERS_TABLE.c.id
                == foreign(PHONE_NUMBER_TABLE.c.customer_id)
            ),
            back_populates="_customer",
            cascade="all, delete-orphan",
            lazy="selectin",
        ),
        "_delivery_addresses": relationship(
            Address,
            primaryjoin=and_(
                CUSTOMERS_TABLE.c.id == foreign(ADDRESSES_TABLE.c.customer_id)
            ),
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
        "_customer_id": ADDRESSES_TABLE.c.customer_id,
        "_shop_id": ADDRESSES_TABLE.c.shop_id,
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
                foreign(ADDRESSES_TABLE.c.customer_id) == CUSTOMERS_TABLE.c.id
            ),
            back_populates="_delivery_addresses",
        ),
    },
)

MAPPER_REGISTRY.map_imperatively(
    PhoneNumber,
    PHONE_NUMBER_TABLE,
    properties={
        "_entity_id": PHONE_NUMBER_TABLE.c.id,
        "_customer_id": PHONE_NUMBER_TABLE.c.customer_id,
        "_shop_id": PHONE_NUMBER_TABLE.c.shop_id,
        "_number": PHONE_NUMBER_TABLE.c.number,
        "_is_primary": PHONE_NUMBER_TABLE.c.is_primary,
        "_customer": relationship(
            Customer,
            primaryjoin=and_(
                foreign(PHONE_NUMBER_TABLE.c.customer_id)
                == CUSTOMERS_TABLE.c.id
            ),
            back_populates="_contacts",
        ),
    },
)
