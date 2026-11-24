from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProcedureBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    description: str | None = None
    duration_minutes: int = Field(..., gt=0)
    price: Decimal = Field(..., ge=0, decimal_places=2)
    is_active: bool = True


class ProcedureCreate(ProcedureBase):
    pass


class ProcedureUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = None
    duration_minutes: int | None = Field(default=None, gt=0)
    price: Decimal | None = Field(default=None, ge=0, decimal_places=2)
    is_active: bool | None = None


class ProcedureResponse(ProcedureBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None