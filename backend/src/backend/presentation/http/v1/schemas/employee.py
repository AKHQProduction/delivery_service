from pydantic import BaseModel

from backend.application.vars import ShopRole


class EditEmployeeSchema(BaseModel):
    name: str | None = None
    role: ShopRole | None = None
