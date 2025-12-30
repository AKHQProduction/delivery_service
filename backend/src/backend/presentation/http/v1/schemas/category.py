from pydantic import BaseModel


class EditCategorySchema(BaseModel):
    name: str | None = None
