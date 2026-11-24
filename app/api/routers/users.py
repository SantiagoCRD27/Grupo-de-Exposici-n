from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_auth_service, get_current_user, require_roles
from app.domain.enums.user_role import UserRole
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.auth_service import AuthService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=list[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 100,
    _: User = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN)),
    auth_service: AuthService = Depends(get_auth_service),
) -> list[User]:
    return auth_service.user_repo.list_all(skip=skip, limit=limit)


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: UserCreate,
    _: User = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN)),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    return auth_service.register(user_in)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    if (
        current_user.id != user_id
        and current_user.role not in (UserRole.SUPER_ADMIN, UserRole.ADMIN)
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para consultar este usuario",
        )
    user = auth_service.user_repo.get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    return user


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    if (
        current_user.id != user_id
        and current_user.role not in (UserRole.SUPER_ADMIN, UserRole.ADMIN)
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para actualizar este usuario",
        )
    user = auth_service.user_repo.get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    if user_in.email is not None:
        existing = auth_service.user_repo.get_by_email(user_in.email)
        if existing is not None and existing.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo ya está registrado por otro usuario",
            )
    if user_in.is_active is not None and current_user.role not in (
        UserRole.SUPER_ADMIN,
        UserRole.ADMIN,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para cambiar el estado del usuario",
        )
    return auth_service.user_repo.update(user=user, user_in=user_in)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    _: User = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN)),
    auth_service: AuthService = Depends(get_auth_service),
) -> None:
    user = auth_service.user_repo.get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    auth_service.user_repo.delete(user)