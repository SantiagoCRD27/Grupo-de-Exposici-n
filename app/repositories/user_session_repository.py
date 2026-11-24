from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user_session import UserSession


class UserSessionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_jti(self, jti: str) -> UserSession | None:
        stmt = select(UserSession).where(UserSession.jti == jti)
        return self.db.scalar(stmt)

    def get_active_by_jti(self, jti: str, now: datetime) -> UserSession | None:
        stmt = select(UserSession).where(
            UserSession.jti == jti,
            UserSession.is_active.is_(True),
            UserSession.revoked_at.is_(None),
            UserSession.expires_at > now,
        )
        return self.db.scalar(stmt)

    def list_by_user(self, user_id: int) -> list[UserSession]:
        stmt = (
            select(UserSession)
            .where(UserSession.user_id == user_id)
            .order_by(UserSession.created_at.desc())
        )
        return list(self.db.scalars(stmt).all())

    def create(
        self,
        user_id: int,
        jti: str,
        expires_at: datetime,
        last_activity_at: datetime,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> UserSession:
        session = UserSession(
            user_id=user_id,
            jti=jti,
            expires_at=expires_at,
            last_activity_at=last_activity_at,
            revoked_at=None,
            is_active=True,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def touch_activity(self, session: UserSession, activity_at: datetime) -> UserSession:
        session.last_activity_at = activity_at
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def revoke(self, session: UserSession, revoked_at: datetime) -> UserSession:
        session.revoked_at = revoked_at
        session.is_active = False
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session