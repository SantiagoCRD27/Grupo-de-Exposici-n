from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.domain.enums.user_role import UserRole
from app.infrastructure.database.session import get_db
from app.models.user import User
from app.models.user_session import UserSession
from app.repositories.user_repository import UserRepository
from app.repositories.user_session_repository import UserSessionRepository
from app.services.auth_service import AuthService

bearer_scheme = HTTPBearer(auto_error=False)


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    user_repo = UserRepository(db)
    session_repo = UserSessionRepository(db)
    return AuthService(user_repo=user_repo, session_repo=session_repo)


def get_current_auth_context(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> tuple[User, UserSession]:
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return auth_service.get_current_user_and_session(credentials.credentials)


def get_current_user(
    auth_ctx: tuple[User, UserSession] = Depends(get_current_auth_context),
) -> User:
    user, _ = auth_ctx
    return user


def get_current_session(
    auth_ctx: tuple[User, UserSession] = Depends(get_current_auth_context),
) -> UserSession:
    _, session = auth_ctx
    return session


def require_roles(*allowed_roles: UserRole):
    def _role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para realizar esta acción",
            )
        return current_user

    return _role_checker


def get_client_ip(request: Request) -> str | None:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    if request.client:
        return request.client.host
    return None