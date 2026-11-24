from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.domain.enums.user_role import UserRole
from app.infrastructure.database.session import get_db
from app.models.user import User
from app.repositories.appointment_repository import AppointmentRepository
from app.repositories.procedure_repository import ProcedureRepository
from app.repositories.user_repository import UserRepository
from app.schemas.appointment import AppointmentCreate, AppointmentResponse, AppointmentUpdate
from app.services.appointment_service import AppointmentService

router = APIRouter(prefix="/appointments", tags=["Appointments"])


def get_appointment_service(db: Session = Depends(get_db)) -> AppointmentService:
    return AppointmentService(
        appointment_repo=AppointmentRepository(db),
        user_repo=UserRepository(db),
        procedure_repo=ProcedureRepository(db),
    )


@router.get("/", response_model=list[AppointmentResponse])
def list_appointments(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    service: AppointmentService = Depends(get_appointment_service),
):
    if current_user.role in (UserRole.SUPER_ADMIN, UserRole.ADMIN):
        return service.appointment_repo.list_all(skip=skip, limit=limit)
    if current_user.role == UserRole.CLIENTE:
        return service.appointment_repo.list_by_client(current_user.id)
    return service.appointment_repo.list_by_employee(current_user.id)


@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def create_appointment(
    appointment_in: AppointmentCreate,
    current_user: User = Depends(get_current_user),
    service: AppointmentService = Depends(get_appointment_service),
):
    if (
        current_user.role == UserRole.CLIENTE
        and appointment_in.client_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes crear citas para otro cliente",
        )
    return service.create(appointment_in)


@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(
    appointment_id: int,
    current_user: User = Depends(get_current_user),
    service: AppointmentService = Depends(get_appointment_service),
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
            detail="No tienes permisos para consultar esta cita",
        )
    return appointment


@router.patch("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(
    appointment_id: int,
    appointment_in: AppointmentUpdate,
    current_user: User = Depends(get_current_user),
    service: AppointmentService = Depends(get_appointment_service),
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
            detail="No tienes permisos para actualizar esta cita",
        )
    return service.update(appointment, appointment_in)


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment(
    appointment_id: int,
    _: User = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN)),
    service: AppointmentService = Depends(get_appointment_service),
) -> None:
    appointment = service.appointment_repo.get_by_id(appointment_id)
    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cita no encontrada",
        )
    service.appointment_repo.delete(appointment)