from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        stmt = select(User).where(User.id == user_id)
        return self.db.scalar(stmt)

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email.lower().strip())
        return self.db.scalar(stmt)

    def list_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        stmt = select(User).offset(skip).limit(limit)
        return list(self.db.scalars(stmt).all())

    def create(self, user_in: UserCreate, password_hash: str) -> User:
        user = User(
            first_name=user_in.first_name.strip(),
            last_name=user_in.last_name.strip(),
            email=user_in.email.lower().strip(),
            phone=user_in.phone.strip() if user_in.phone else None,
            password_hash=password_hash,
            role=user_in.role,
            is_active=True,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user: User, user_in: UserUpdate) -> User:
        data = user_in.model_dump(exclude_unset=True)
        if "first_name" in data and data["first_name"] is not None:
            user.first_name = data["first_name"].strip()
        if "last_name" in data and data["last_name"] is not None:
            user.last_name = data["last_name"].strip()
        if "email" in data and data["email"] is not None:
            user.email = data["email"].lower().strip()
        if "phone" in data:
            user.phone = data["phone"].strip() if data["phone"] else None
        if "is_active" in data and data["is_active"] is not None:
            user.is_active = data["is_active"]
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user: User) -> None:
        self.db.delete(user)
        self.db.commit()