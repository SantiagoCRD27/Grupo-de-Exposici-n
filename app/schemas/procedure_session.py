from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProcedureSessionBase(BaseModel):
    session_number: int = Field(..., gt=0)
    scheduled_at: datetime | None = None
    completed_at: datetime | None = None
    notes: str | None = None


class ProcedureSessionCreate(ProcedureSessionBase):
    appointment_id: int


class ProcedureSessionUpdate(BaseModel):
    session_number: int | None = Field(default=None, gt=0)
    scheduled_at: datetime | None = None
    completed_at: datetime | None = None
    notes: str | None = None


class ProcedureSessionResponse(ProcedureSessionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    appointment_id: int
    created_at: datetime