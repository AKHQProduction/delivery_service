from uuid import UUID

from pydantic import BaseModel

from backend.application.vars import Empty


class EditProductSchema(BaseModel):
    name: str | None = None
    price: int | None = None
    category_id: UUID | Empty | None = None
