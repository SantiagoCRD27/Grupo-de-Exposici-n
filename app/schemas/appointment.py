from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.domain.enums.appointment_status import AppointmentStatus


class AppointmentBase(BaseModel):
    client_id: int
    procedure_id: int
    employee_id: int | None = None
    start_at: datetime
    end_at: datetime
    status: AppointmentStatus = AppointmentStatus.PENDIENTE
    cancellation_reason: str | None = None
    cancellation_penalty: Decimal = Decimal("0.00")


class AppointmentCreate(AppointmentBase):
    pass


class AppointmentUpdate(BaseModel):
    client_id: int | None = None
    procedure_id: int | None = None
    employee_id: int | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    status: AppointmentStatus | None = None
    cancellation_reason: str | None = None
    cancellation_penalty: Decimal | None = None


class AppointmentResponse(AppointmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cancelled_at: datetime | None = None
    created_at: datetime
    updated_at: datetime