from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.domain.enums.user_role import UserRole
from app.infrastructure.database.session import get_db
from app.models.user import User
from app.repositories.client_profile_repository import ClientProfileRepository
from app.repositories.user_repository import UserRepository
from app.schemas.client_profile import ClientProfileCreate, ClientProfileResponse, ClientProfileUpdate
from app.services.client_profile_service import ClientProfileService

router = APIRouter(prefix="/client-profiles", tags=["Client Profiles"])


def get_client_profile_service(db: Session = Depends(get_db)) -> ClientProfileService:
    return ClientProfileService(
        profile_repo=ClientProfileRepository(db),
        user_repo=UserRepository(db),
    )


@router.get("/", response_model=list[ClientProfileResponse])
def list_client_profiles(
    skip: int = 0,
    limit: int = 100,
    _: User = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN)),
    service: ClientProfileService = Depends(get_client_profile_service),
):
    return service.profile_repo.list_all(skip=skip, limit=limit)


@router.post("/", response_model=ClientProfileResponse, status_code=status.HTTP_201_CREATED)
def create_client_profile(
    profile_in: ClientProfileCreate,
    current_user: User = Depends(get_current_user),
    service: ClientProfileService = Depends(get_client_profile_service),
):
    if (
        current_user.id != profile_in.user_id
        and current_user.role not in (UserRole.SUPER_ADMIN, UserRole.ADMIN)
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para crear este perfil de cliente",
        )
    return service.create(profile_in)


@router.get("/{profile_id}", response_model=ClientProfileResponse)
def get_client_profile(
    profile_id: int,
    current_user: User = Depends(get_current_user),
    service: ClientProfileService = Depends(get_client_profile_service),
):
    profile = service.profile_repo.get_by_id(profile_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil de cliente no encontrado",
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


@router.get("/user/{user_id}", response_model=ClientProfileResponse)
def get_client_profile_by_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    service: ClientProfileService = Depends(get_client_profile_service),
):
    if (
        current_user.id != user_id
        and current_user.role not in (UserRole.SUPER_ADMIN, UserRole.ADMIN)
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para consultar este perfil",
        )
    profile = service.profile_repo.get_by_user_id(user_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil de cliente no encontrado",
        )
    return profile


@router.patch("/{profile_id}", response_model=ClientProfileResponse)
def update_client_profile(
    profile_id: int,
    profile_in: ClientProfileUpdate,
    current_user: User = Depends(get_current_user),
    service: ClientProfileService = Depends(get_client_profile_service),
):
    profile = service.profile_repo.get_by_id(profile_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil de cliente no encontrado",
        )
    if (
        current_user.id != profile.user_id
        and current_user.role not in (UserRole.SUPER_ADMIN, UserRole.ADMIN)
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para actualizar este perfil",
        )
    return service.update(profile, profile_in)


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client_profile(
    profile_id: int,
    _: User = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN)),
    service: ClientProfileService = Depends(get_client_profile_service),
) -> None:
    profile = service.profile_repo.get_by_id(profile_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil de cliente no encontrado",
        )
    service.profile_repo.delete(profile)