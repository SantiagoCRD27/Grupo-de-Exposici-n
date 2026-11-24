from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class EmployeeProfileBase(BaseModel):
    job_title: str = Field(..., min_length=1, max_length=100)
    specialty: str | None = Field(default=None, max_length=150)
    hire_date: date | None = None
    is_available: bool = True
    notes: str | None = None


class EmployeeProfileCreate(EmployeeProfileBase):
    user_id: int


class EmployeeProfileUpdate(BaseModel):
    job_title: str | None = Field(default=None, min_length=1, max_length=100)
    specialty: str | None = Field(default=None, max_length=150)
    hire_date: date | None = None
    is_available: bool | None = None
    notes: str | None = None


class EmployeeProfileResponse(EmployeeProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int