from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate


class AppointmentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, appointment_id: int) -> Appointment | None:
        stmt = select(Appointment).where(Appointment.id == appointment_id)
        return self.db.scalar(stmt)

    def list_all(self, skip: int = 0, limit: int = 100) -> list[Appointment]:
        stmt = (
            select(Appointment)
            .order_by(Appointment.start_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def list_by_client(self, client_id: int) -> list[Appointment]:
        stmt = (
            select(Appointment)
            .where(Appointment.client_id == client_id)
            .order_by(Appointment.start_at.desc())
        )
        return list(self.db.scalars(stmt).all())

    def list_by_employee(self, employee_id: int) -> list[Appointment]:
        stmt = (
            select(Appointment)
            .where(Appointment.employee_id == employee_id)
            .order_by(Appointment.start_at.desc())
        )
        return list(self.db.scalars(stmt).all())

    def create(self, appointment_in: AppointmentCreate) -> Appointment:
        appointment = Appointment(**appointment_in.model_dump())
        self.db.add(appointment)
        self.db.commit()
        self.db.refresh(appointment)
        return appointment

    def update(self, appointment: Appointment, appointment_in: AppointmentUpdate) -> Appointment:
        data = appointment_in.model_dump(exclude_unset=True)
        for field, value in data.items():
            setattr(appointment, field, value)
        self.db.add(appointment)
        self.db.commit()
        self.db.refresh(appointment)
        return appointment

    def delete(self, appointment: Appointment) -> None:
        self.db.delete(appointment)
        self.db.commit()