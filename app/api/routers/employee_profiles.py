from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.domain.enums.user_role import UserRole
from app.infrastructure.database.session import get_db
from app.models.user import User
from app.repositories.employee_profile_repository import EmployeeProfileRepository
from app.repositories.user_repository import UserRepository
from app.schemas.employee_profile import (
    EmployeeProfileCreate,
    EmployeeProfileResponse,
    EmployeeProfileUpdate,
)
from app.services.employee_profile_service import EmployeeProfileService

router = APIRouter(prefix="/employee-profiles", tags=["Employee Profiles"])


def get_employee_profile_service(db: Session = Depends(get_db)) -> EmployeeProfileService:
    return EmployeeProfileService(
        profile_repo=EmployeeProfileRepository(db),
        user_repo=UserRepository(db),
    )


@router.get("/", response_model=list[EmployeeProfileResponse])
def list_employee_profiles(
    skip: int = 0,
    limit: int = 100,
    _: User = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN)),
    service: EmployeeProfileService = Depends(get_employee_profile_service),
):
    return service.profile_repo.list_all(skip=skip, limit=limit)


@router.post("/", response_model=EmployeeProfileResponse, status_code=status.HTTP_201_CREATED)
def create_employee_profile(
    profile_in: EmployeeProfileCreate,
    _: User = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN)),
    service: EmployeeProfileService = Depends(get_employee_profile_service),
):
    return service.create(profile_in)


@router.get("/{profile_id}", response_model=EmployeeProfileResponse)
def get_employee_profile(
    profile_id: int,
    current_user: User = Depends(get_current_user),
    service: EmployeeProfileService = Depends(get_employee_profile_service),
):
    profile = service.profile_repo.get_by_id(profile_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil de empleado no encontrado",
        )
    if (
        current_user.id != profile.user_id
        and current_user.role not in (UserRole.SUPER_ADMIN, UserRole.ADMIN)
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para consultar este perfil",
        )
    return profile


@router.patch("/{profile_id}", response_model=EmployeeProfileResponse)
def update_employee_profile(
    profile_id: int,
    profile_in: EmployeeProfileUpdate,
    _: User = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN)),
    service: EmployeeProfileService = Depends(get_employee_profile_service),
):
    profile = service.profile_repo.get_by_id(profile_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil de empleado no encontrado",
        )
    return service.update(profile, profile_in)


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee_profile(
    profile_id: int,
    _: User = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN)),
    service: EmployeeProfileService = Depends(get_employee_profile_service),
) -> None:
    profile = service.profile_repo.get_by_id(profile_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil de empleado no encontrado",
        )
    service.profile_repo.delete(profile)