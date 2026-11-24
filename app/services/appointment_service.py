from datetime import datetime, timezone
from fastapi import HTTPException, status

from app.domain.enums.appointment_status import AppointmentStatus
from app.models.appointment import Appointment
from app.repositories.appointment_repository import AppointmentRepository
from app.repositories.procedure_repository import ProcedureRepository
from app.repositories.user_repository import UserRepository
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate


class AppointmentService:
    def __init__(
        self,
        appointment_repo: AppointmentRepository,
        user_repo: UserRepository,
        procedure_repo: ProcedureRepository,
    ) -> None:
        self.appointment_repo = appointment_repo
        self.user_repo = user_repo
        self.procedure_repo = procedure_repo

    def _validate_references(
        self,
        client_id: int,
        procedure_id: int,
        employee_id: int | None,
        start_at,
        end_at,
    ) -> None:
        if end_at <= start_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La hora de fin debe ser posterior a la hora de inicio",
            )
        client = self.user_repo.get_by_id(client_id)
        if client is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente no encontrado",
            )
        if employee_id is not None:
            employee = self.user_repo.get_by_id(employee_id)
            if employee is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Empleado no encontrado",
                )
        procedure = self.procedure_repo.get_by_id(procedure_id)
        if procedure is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Procedimiento no encontrado",
            )

    @staticmethod
    def _now_utc_naive() -> datetime:
        return datetime.now(timezone.utc).replace(tzinfo=None)

    def create(self, appointment_in: AppointmentCreate) -> Appointment:
        self._validate_references(
            client_id=appointment_in.client_id,
            procedure_id=appointment_in.procedure_id,
            employee_id=appointment_in.employee_id,
            start_at=appointment_in.start_at,
            end_at=appointment_in.end_at,
        )
        created = self.appointment_repo.create(appointment_in)
        if created.status == AppointmentStatus.CANCELADA and created.cancelled_at is None:
            return self.appointment_repo.update(
                appointment=created,
                appointment_in=AppointmentUpdate.model_construct(
                    cancelled_at=self._now_utc_naive()
                ),
            )
        return created

    def update(self, appointment: Appointment, appointment_in: AppointmentUpdate) -> Appointment:
        data = appointment_in.model_dump(exclude_unset=True)
        client_id = data.get("client_id", appointment.client_id)
        procedure_id = data.get("procedure_id", appointment.procedure_id)
        employee_id = data.get("employee_id", appointment.employee_id)
        start_at = data.get("start_at", appointment.start_at)
        end_at = data.get("end_at", appointment.end_at)
        self._validate_references(
            client_id=client_id,
            procedure_id=procedure_id,
            employee_id=employee_id,
            start_at=start_at,
            end_at=end_at,
        )

        if "status" in data:
            new_status = data["status"]
            if new_status == AppointmentStatus.CANCELADA:
                if appointment.status != AppointmentStatus.CANCELADA or appointment.cancelled_at is None:
                    appointment.cancelled_at = self._now_utc_naive()
            else:
                appointment.cancelled_at = None

        return self.appointment_repo.update(appointment=appointment, appointment_in=appointment_in)