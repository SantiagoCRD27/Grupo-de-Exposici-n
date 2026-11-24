from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.client_profile import ClientProfile
from app.schemas.client_profile import ClientProfileCreate, ClientProfileUpdate


class ClientProfileRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, profile_id: int) -> ClientProfile | None:
        stmt = select(ClientProfile).where(ClientProfile.id == profile_id)
        return self.db.scalar(stmt)

    def get_by_user_id(self, user_id: int) -> ClientProfile | None:
        stmt = select(ClientProfile).where(ClientProfile.user_id == user_id)
        return self.db.scalar(stmt)

    def list_all(self, skip: int = 0, limit: int = 100) -> list[ClientProfile]:
        stmt = select(ClientProfile).offset(skip).limit(limit)
        return list(self.db.scalars(stmt).all())

    def create(self, profile_in: ClientProfileCreate) -> ClientProfile:
        profile = ClientProfile(**profile_in.model_dump())
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def update(self, profile: ClientProfile, profile_in: ClientProfileUpdate) -> ClientProfile:
        data = profile_in.model_dump(exclude_unset=True)
        for field, value in data.items():
            setattr(profile, field, value)
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def delete(self, profile: ClientProfile) -> None:
        self.db.delete(profile)
        self.db.commit()