from uuid import UUID

from pydantic import BaseModel


class EditProductSchema(BaseModel):
    name: str | None = None
    price: int | None = None
    category_id: UUID | None = None
