from pydantic import BaseModel

from backend.application.vars import ProductCategory


class EditProductSchema(BaseModel):
    name: str | None = None
    price: int | None = None
    category: ProductCategory | None = None
