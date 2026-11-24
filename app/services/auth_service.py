from datetime import datetime, timezone

from fastapi import HTTPException, status

from app.core.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)
from app.models.user import User
from app.models.user_session import UserSession
from app.repositories.user_repository import UserRepository
from app.repositories.user_session_repository import UserSessionRepository
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserCreate


class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        session_repo: UserSessionRepository,
    ) -> None:
        self.user_repo = user_repo
        self.session_repo = session_repo

    def register(self, user_in: UserCreate) -> User:
        existing = self.user_repo.get_by_email(user_in.email)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo ya está registrado",
            )
        password_hash = get_password_hash(user_in.password)
        return self.user_repo.create(user_in=user_in, password_hash=password_hash)

    def login(
        self,
        login_data: LoginRequest,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> TokenResponse:
        user = self.user_repo.get_by_email(login_data.email)
        if user is None or not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario inactivo",
            )

        access_token, jti, expires_at = create_access_token(
            subject=str(user.id),
            role=user.role.value,
        )
        now_naive = datetime.now(timezone.utc).replace(tzinfo=None)

        self.session_repo.create(
            user_id=user.id,
            jti=jti,
            expires_at=expires_at,
            last_activity_at=now_naive,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_at=expires_at,
        )

    def get_current_user_and_session(self, token: str) -> tuple[User, UserSession]:
        payload = decode_access_token(token)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido o expirado",
                headers={"WWW-Authenticate": "Bearer"},
            )

        sub = payload.get("sub")
        jti = payload.get("jti")
        if not sub or not jti:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token incompleto",
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            user_id = int(sub)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Sujeto de token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc

        now_naive = datetime.now(timezone.utc).replace(tzinfo=None)
        session = self.session_repo.get_active_by_jti(jti=jti, now=now_naive)
        if session is None or session.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Sesión inválida, expirada o revocada",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = self.user_repo.get_by_id(user_id)
        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado o inactivo",
                headers={"WWW-Authenticate": "Bearer"},
            )

        self.session_repo.touch_activity(session=session, activity_at=now_naive)
        return user, session

    def logout(self, token: str) -> None:
        payload = decode_access_token(token)
        jti = payload.get("jti") if payload else None
        if not jti:
            return
        session = self.session_repo.get_by_jti(jti=jti)
        if session is not None and session.is_active:
            now_naive = datetime.now(timezone.utc).replace(tzinfo=None)
            self.session_repo.revoke(session=session, revoked_at=now_naive)