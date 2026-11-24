from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base


class ProcedureSession(Base):
    __tablename__ = "procedure_sessions"

    __table_args__ = (
        UniqueConstraint(
            "procedure_id",
            "session_number",
            name="uq_procedure_session_number"
        ),
        CheckConstraint(
            "session_number > 0",
            name="ck_procedure_session_number_positive"
        ),
        CheckConstraint(
            "duration_minutes > 0",
            name="ck_procedure_session_duration_positive"
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    procedure_id: Mapped[int] = mapped_column(
        ForeignKey("procedures.id", ondelete="CASCADE"),
        nullable=False
    )

    session_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    title: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    duration_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    procedure = relationship(
        "Procedure",
        back_populates="procedure_sessions"
    )