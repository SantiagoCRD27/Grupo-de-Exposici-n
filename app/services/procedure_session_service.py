from fastapi import HTTPException, status

from app.models.procedure_session import ProcedureSession
from app.repositories.appointment_repository import AppointmentRepository
from app.repositories.procedure_session_repository import ProcedureSessionRepository
from app.schemas.procedure_session import ProcedureSessionCreate, ProcedureSessionUpdate


class ProcedureSessionService:
    def __init__(
        self,
        session_repo: ProcedureSessionRepository,
        appointment_repo: AppointmentRepository,
    ) -> None:
        self.session_repo = session_repo
        self.appointment_repo = appointment_repo

    def create(self, session_in: ProcedureSessionCreate) -> ProcedureSession:
        appointment = self.appointment_repo.get_by_id(session_in.appointment_id)
        if appointment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cita no encontrada",
            )
        return self.session_repo.create(session_in)

    def update(
        self,
        proc_session: ProcedureSession,
        session_in: ProcedureSessionUpdate,
    ) -> ProcedureSession:
        return self.session_repo.update(proc_session=proc_session, session_in=session_in)