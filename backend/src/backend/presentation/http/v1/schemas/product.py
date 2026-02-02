from decimal import Decimal

from pydantic import BaseModel


class EditProductSchema(BaseModel):
    name: str | None = None
    price: Decimal | None = None
    category_id: str | None = None
