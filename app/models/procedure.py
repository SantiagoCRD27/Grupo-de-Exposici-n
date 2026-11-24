from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Integer,
    String,
    Text,
    Numeric,
    Boolean,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base


class Procedure(Base):
    __tablename__ = "procedures"

    __table_args__ = (
        CheckConstraint(
            "duration_minutes > 0",
            name="ck_procedures_duration_positive"
        ),
        CheckConstraint(
            "price >= 0",
            name="ck_procedures_price_nonnegative"
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        unique=True
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    duration_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )

    procedure_sessions = relationship(
        "ProcedureSession",
        back_populates="procedure",
        cascade="all, delete-orphan",
        order_by="ProcedureSession.session_number"
    )

    appointments = relationship(
        "Appointment",
        back_populates="procedure",
        passive_deletes=True
    )