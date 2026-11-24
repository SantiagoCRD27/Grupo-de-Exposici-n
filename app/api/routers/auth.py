from fastapi import APIRouter, Depends, Request, status
from fastapi.security import HTTPAuthorizationCredentials

from app.api.deps import (
    bearer_scheme,
    get_auth_service,
    get_client_ip,
    get_current_session,
    get_current_user,
)
from app.models.user import User
from app.models.user_session import UserSession
from app.repositories.user_repository import UserRepository
from app.schemas.auth import CurrentUserResponse, LoginRequest, SessionResponse, TokenResponse
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_in: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    return auth_service.register(user_in)


@router.post("/login", response_model=TokenResponse)
def login(
    login_data: LoginRequest,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    return auth_service.login(
        login_data=login_data,
        ip_address=get_client_ip(request),
        user_agent=request.headers.get("user-agent"),
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> None:
    if credentials and credentials.credentials:
        auth_service.logout(credentials.credentials)


@router.get("/me", response_model=CurrentUserResponse)
def get_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.get("/sessions", response_model=list[SessionResponse])
def list_my_sessions(
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> list[UserSession]:
    return auth_service.session_repo.list_by_user(current_user.id)


@router.get("/current-session", response_model=SessionResponse)
def get_my_current_session(
    current_session: UserSession = Depends(get_current_session),
) -> UserSession:
    return current_session