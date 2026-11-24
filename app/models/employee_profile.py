from datetime import date

from sqlalchemy import (
    Date,
    ForeignKey,
    Integer,
    String,
    Boolean,
    Text,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base


class EmployeeProfile(Base):
    __tablename__ = "employee_profiles"

    __table_args__ = (
        Index("ix_employee_profiles_available", "is_available"),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )

    job_title: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    specialty: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    hire_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    is_available: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    user = relationship(
        "User",
        back_populates="employee_profile"
    )

    appointments = relationship(
        "Appointment",
        back_populates="employee",
        passive_deletes=True
    )