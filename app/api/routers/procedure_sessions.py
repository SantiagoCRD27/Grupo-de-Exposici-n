from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.domain.enums.user_role import UserRole
from app.infrastructure.database.session import get_db
from app.models.user import User
from app.repositories.appointment_repository import AppointmentRepository
from app.repositories.procedure_session_repository import ProcedureSessionRepository
from app.schemas.procedure_session import (
    ProcedureSessionCreate,
    ProcedureSessionResponse,
    ProcedureSessionUpdate,
)
from app.services.procedure_session_service import ProcedureSessionService

router = APIRouter(prefix="/procedure-sessions", tags=["Procedure Sessions"])


def get_procedure_session_service(db: Session = Depends(get_db)) -> ProcedureSessionService:
    return ProcedureSessionService(
        session_repo=ProcedureSessionRepository(db),
        appointment_repo=AppointmentRepository(db),
    )


@router.get("/appointment/{appointment_id}", response_model=list[ProcedureSessionResponse])
def list_sessions_by_appointment(
    appointment_id: int,
    current_user: User = Depends(get_current_user),
    service: ProcedureSessionService = Depends(get_procedure_session_service),
):
    appointment = service.appointment_repo.get_by_id(appointment_id)
    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cita no encontrada",
        )
    if (
        current_user.role not in (UserRole.SUPER_ADMIN, UserRole.ADMIN)
        and current_user.id not in (appointment.client_id, appointment.employee_id)
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver estas sesiones",
        )
    return service.session_repo.list_by_appointment(appointment_id)


@router.post("/", response_model=ProcedureSessionResponse, status_code=status.HTTP_201_CREATED)
def create_procedure_session(
    session_in: ProcedureSessionCreate,
    _: User = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN)),
    service: ProcedureSessionService = Depends(get_procedure_session_service),
):
    return service.create(session_in)


@router.patch("/{session_id}", response_model=ProcedureSessionResponse)
def update_procedure_session(
    session_id: int,
    session_in: ProcedureSessionUpdate,
    _: User = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN)),
    service: ProcedureSessionService = Depends(get_procedure_session_service),
):
    proc_session = service.session_repo.get_by_id(session_id)
    if proc_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sesión de procedimiento no encontrada",
        )
    return service.update(proc_session, session_in)


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_procedure_session(
    session_id: int,
    _: User = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN)),
    service: ProcedureSessionService = Depends(get_procedure_session_service),
) -> None:
    proc_session = service.session_repo.get_by_id(session_id)
    if proc_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sesión de procedimiento no encontrada",
        )
    service.session_repo.delete(proc_session)