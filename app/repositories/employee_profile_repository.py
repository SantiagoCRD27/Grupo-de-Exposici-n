from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.employee_profile import EmployeeProfile
from app.schemas.employee_profile import EmployeeProfileCreate, EmployeeProfileUpdate


class EmployeeProfileRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, profile_id: int) -> EmployeeProfile | None:
        stmt = select(EmployeeProfile).where(EmployeeProfile.id == profile_id)
        return self.db.scalar(stmt)

    def get_by_user_id(self, user_id: int) -> EmployeeProfile | None:
        stmt = select(EmployeeProfile).where(EmployeeProfile.user_id == user_id)
        return self.db.scalar(stmt)

    def list_all(self, skip: int = 0, limit: int = 100) -> list[EmployeeProfile]:
        stmt = select(EmployeeProfile).offset(skip).limit(limit)
        return list(self.db.scalars(stmt).all())

    def create(self, profile_in: EmployeeProfileCreate) -> EmployeeProfile:
        profile = EmployeeProfile(**profile_in.model_dump())
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def update(self, profile: EmployeeProfile, profile_in: EmployeeProfileUpdate) -> EmployeeProfile:
        data = profile_in.model_dump(exclude_unset=True)
        for field, value in data.items():
            setattr(profile, field, value)
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def delete(self, profile: EmployeeProfile) -> None:
        self.db.delete(profile)
        self.db.commit()