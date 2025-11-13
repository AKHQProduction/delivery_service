from pydantic import BaseModel


class ErrorSchema(BaseModel):
    detail: str
