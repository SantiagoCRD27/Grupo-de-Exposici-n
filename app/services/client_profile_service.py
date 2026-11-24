from fastapi import HTTPException, status

from app.models.client_profile import ClientProfile
from app.repositories.client_profile_repository import ClientProfileRepository
from app.repositories.user_repository import UserRepository
from app.schemas.client_profile import ClientProfileCreate, ClientProfileUpdate


class ClientProfileService:
    def __init__(
        self,
        profile_repo: ClientProfileRepository,
        user_repo: UserRepository,
    ) -> None:
        self.profile_repo = profile_repo
        self.user_repo = user_repo

    def create(self, profile_in: ClientProfileCreate) -> ClientProfile:
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
                detail="El usuario ya tiene un perfil de cliente",
            )
        return self.profile_repo.create(profile_in)

    def update(self, profile: ClientProfile, profile_in: ClientProfileUpdate) -> ClientProfile:
        return self.profile_repo.update(profile=profile, profile_in=profile_in)