import sqlalchemy as sa
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship

from entities.employee.models import Employee, EmployeeRole
from infrastructure.persistence.models import mapper_registry

employees_table = sa.Table(
    "employees",
    mapper_registry.metadata,
    sa.Column("employee_id", sa.Integer, primary_key=True, unique=True),
    sa.Column(
        "user_id",
        sa.BigInteger,
        sa.ForeignKey("users.user_id", ondelete="CASCADE"),
    ),
    sa.Column(
        "shop_id",
        sa.BigInteger,
        sa.ForeignKey("shops.shop_id", ondelete="CASCADE"),
    ),
    sa.Column("role", sa.Enum(EmployeeRole), nullable=False),
    sa.Column(
        "created_at",
        sa.DateTime,
        default=sa.func.now(),
        server_default=sa.func.now(),
    ),
    sa.Column(
        "updated_at",
        sa.DateTime,
        default=sa.func.now(),
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
        server_onupdate=sa.func.now(),
    ),
    UniqueConstraint("user_id", name="uq_shop_employee"),
)


def map_employee_table() -> None:
    mapper_registry.map_imperatively(
        Employee,
        employees_table,
        properties={
            "user": relationship("User", back_populates="employees"),
            "shop": relationship("Shop", back_populates="employees"),
        },
    )
