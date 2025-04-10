import sqlalchemy as sa
from sqlalchemy import and_
from sqlalchemy.orm import relationship

from delivery_service.domain.shared.vo.location import Coordinates
from delivery_service.domain.shops.shop import Shop
from delivery_service.domain.shops.value_objects import DaysOff
from delivery_service.domain.staff.staff_member import StaffMember
from delivery_service.domain.staff.staff_role import RoleCollection
from delivery_service.infrastructure.persistence.tables.base import (
    MAPPER_REGISTRY,
    value_object_to_json,
)
from delivery_service.infrastructure.persistence.tables.users import (
    ROLES_TABLE,
    USERS_TO_ROLES_TABLE,
)

SHOPS_TABLE = sa.Table(
    "shops",
    MAPPER_REGISTRY.metadata,
    sa.Column("id", sa.UUID, primary_key=True, unique=True),
    sa.Column("name", sa.String, nullable=False),
    sa.Column(
        "coordinates", value_object_to_json(Coordinates), nullable=False
    ),
    sa.Column("days_off", value_object_to_json(DaysOff), nullable=False),
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

STAFF_MEMBERS_TABLE = sa.Table(
    "staff_members",
    MAPPER_REGISTRY.metadata,
    sa.Column(
        "user_id",
        sa.UUID,
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    sa.Column(
        "shop_id", sa.UUID, sa.ForeignKey("shops.id", ondelete="CASCADE")
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

MAPPER_REGISTRY.map_imperatively(
    Shop,
    SHOPS_TABLE,
    properties={
        "_entity_id": SHOPS_TABLE.c.id,
        "_name": SHOPS_TABLE.c.name,
        "_coordinates": SHOPS_TABLE.c.coordinates,
        "_days_off": SHOPS_TABLE.c.days_off,
        "_staff_members": relationship(
            StaffMember,
            primaryjoin=and_(
                SHOPS_TABLE.c.id == STAFF_MEMBERS_TABLE.c.shop_id
            ),
            back_populates="_shop",
            cascade="all, delete-orphan",
            lazy="selectin",
        ),
    },
)

MAPPER_REGISTRY.map_imperatively(
    StaffMember,
    STAFF_MEMBERS_TABLE,
    properties={
        "_entity_id": STAFF_MEMBERS_TABLE.c.user_id,
        "_shop_id": STAFF_MEMBERS_TABLE.c.shop_id,
        "_roles": relationship(
            "StaffRole",
            secondary=USERS_TO_ROLES_TABLE,
            primaryjoin=and_(
                STAFF_MEMBERS_TABLE.c.user_id == USERS_TO_ROLES_TABLE.c.user_id
            ),
            secondaryjoin=and_(
                USERS_TO_ROLES_TABLE.c.role_id == ROLES_TABLE.c.id
            ),
            collection_class=RoleCollection,
            lazy="selectin",
        ),
        "_shop": relationship(
            Shop,
            primaryjoin=and_(
                STAFF_MEMBERS_TABLE.c.shop_id == SHOPS_TABLE.c.id
            ),
            back_populates="_staff_members",
        ),
    },
)
