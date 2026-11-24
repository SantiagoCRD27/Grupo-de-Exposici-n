from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.domain.enums.user_role import UserRole
from app.infrastructure.database.session import get_db
from app.models.user import User
from app.repositories.procedure_repository import ProcedureRepository
from app.schemas.procedure import ProcedureCreate, ProcedureResponse, ProcedureUpdate

router = APIRouter(prefix="/procedures", tags=["Procedures"])


def get_procedure_repo(db: Session = Depends(get_db)) -> ProcedureRepository:
    return ProcedureRepository(db)


@router.get("/", response_model=list[ProcedureResponse])
def list_procedures(
    skip: int = 0,
    limit: int = 100,
    only_active: bool = False,
    repo: ProcedureRepository = Depends(get_procedure_repo),
):
    return repo.list_all(skip=skip, limit=limit, only_active=only_active)


@router.get("/{procedure_id}", response_model=ProcedureResponse)
def get_procedure(
    procedure_id: int,
    repo: ProcedureRepository = Depends(get_procedure_repo),
):
    procedure = repo.get_by_id(procedure_id)
    if procedure is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Procedimiento no encontrado",
        )
    return procedure


@router.post("/", response_model=ProcedureResponse, status_code=status.HTTP_201_CREATED)
def create_procedure(
    procedure_in: ProcedureCreate,
    _: User = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN)),
    repo: ProcedureRepository = Depends(get_procedure_repo),
):
    return repo.create(procedure_in)


@router.patch("/{procedure_id}", response_model=ProcedureResponse)
def update_procedure(
    procedure_id: int,
    procedure_in: ProcedureUpdate,
    _: User = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN)),
    repo: ProcedureRepository = Depends(get_procedure_repo),
):
    procedure = repo.get_by_id(procedure_id)
    if procedure is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Procedimiento no encontrado",
        )
    return repo.update(procedure, procedure_in)


@router.delete("/{procedure_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_procedure(
    procedure_id: int,
    _: User = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN)),
    repo: ProcedureRepository = Depends(get_procedure_repo),
) -> None:
    procedure = repo.get_by_id(procedure_id)
    if procedure is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Procedimiento no encontrado",
        )
    repo.delete(procedure)