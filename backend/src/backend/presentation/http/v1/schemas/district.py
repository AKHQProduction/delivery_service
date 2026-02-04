from pydantic import BaseModel


class EditDistrictSchema(BaseModel):
    name: str | None = None
