from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    Numeric,
    Text,
    Index,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums.appointment_status import AppointmentStatus
from app.infrastructure.database.base import Base


class Appointment(Base):
    __tablename__ = "appointments"

    __table_args__ = (
        CheckConstraint(
            "end_at > start_at",
            name="ck_appointments_valid_time"
        ),
        CheckConstraint(
            "cancellation_penalty >= 0",
            name="ck_appointments_penalty_nonnegative"
        ),
        Index(
            "ix_appointments_client_start",
            "client_id",
            "start_at"
        ),
        Index(
            "ix_appointments_employee_start",
            "employee_id",
            "start_at"
        ),
        Index(
            "ix_appointments_status_start",
            "status",
            "start_at"
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    client_id: Mapped[int] = mapped_column(
        ForeignKey("client_profiles.id", ondelete="RESTRICT"),
        nullable=False
    )

    procedure_id: Mapped[int] = mapped_column(
        ForeignKey("procedures.id", ondelete="RESTRICT"),
        nullable=False
    )

    employee_id: Mapped[int | None] = mapped_column(
        ForeignKey("employee_profiles.id", ondelete="SET NULL"),
        nullable=True
    )

    start_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    end_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    status: Mapped[AppointmentStatus] = mapped_column(
        SAEnum(
            AppointmentStatus,
            values_callable=lambda enum_cls: [
                item.value for item in enum_cls
            ],
            native_enum=False,
            create_constraint=True,
            length=20,
            name="appointment_status"
        ),
        nullable=False,
        default=AppointmentStatus.PENDIENTE
    )

    cancellation_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    cancelled_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    cancellation_penalty: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00")
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )

    client = relationship(
        "ClientProfile",
        back_populates="appointments"
    )

    procedure = relationship(
        "Procedure",
        back_populates="appointments"
    )

    employee = relationship(
        "EmployeeProfile",
        back_populates="appointments"
    )