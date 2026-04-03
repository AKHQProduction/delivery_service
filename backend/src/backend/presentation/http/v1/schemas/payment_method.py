from pydantic import BaseModel


class EditPaymentMethodSchema(BaseModel):
    name: str | None = None
