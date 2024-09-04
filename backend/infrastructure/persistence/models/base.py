from sqlalchemy import Column, DateTime, func
from sqlalchemy.orm import registry

mapper_registry = registry()

created_at_column = Column(
        "created_at",
        DateTime,
        default=func.now(),
        server_default=func.now()
)

updated_at_column = Column(
        "updated_at",
        DateTime,
        default=func.now(),
        server_default=func.now(),
        onupdate=func.now(),
        server_onupdate=func.now(),
)
