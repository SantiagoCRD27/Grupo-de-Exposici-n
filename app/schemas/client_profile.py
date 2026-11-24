from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class ClientProfileBase(BaseModel):
    birth_date: date | None = None
    address: str | None = Field(default=None, max_length=255)
    emergency_contact_name: str | None = Field(default=None, max_length=150)
    emergency_contact_phone: str | None = Field(default=None, max_length=30)
    notes: str | None = None


class ClientProfileCreate(ClientProfileBase):
    user_id: int


class ClientProfileUpdate(ClientProfileBase):
    pass


class ClientProfileResponse(ClientProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int