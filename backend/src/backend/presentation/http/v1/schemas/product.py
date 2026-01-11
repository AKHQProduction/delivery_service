from pydantic import BaseModel


class EditProductSchema(BaseModel):
    name: str | None = None
    price: int | None = None
    category_id: str | None = None
