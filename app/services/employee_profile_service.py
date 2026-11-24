from fastapi import HTTPException, status

from app.models.employee_profile import EmployeeProfile
from app.repositories.employee_profile_repository import EmployeeProfileRepository
from app.repositories.user_repository import UserRepository
from app.schemas.employee_profile import EmployeeProfileCreate, EmployeeProfileUpdate


class EmployeeProfileService:
    def __init__(
        self,
        profile_repo: EmployeeProfileRepository,
        user_repo: UserRepository,
    ) -> None:
        self.profile_repo = profile_repo
        self.user_repo = user_repo

    def create(self, profile_in: EmployeeProfileCreate) -> EmployeeProfile:
        user = self.user_repo.get_by_id(profile_in.user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado",
            )
        existing = self.profile_repo.get_by_user_id(profile_in.user_id)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El usuario ya tiene un perfil de empleado",
            )
        return self.profile_repo.create(profile_in)

    def update(self, profile: EmployeeProfile, profile_in: EmployeeProfileUpdate) -> EmployeeProfile:
        return self.profile_repo.update(profile=profile, profile_in=profile_in)