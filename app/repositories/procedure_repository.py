from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.procedure import Procedure
from app.schemas.procedure import ProcedureCreate, ProcedureUpdate


class ProcedureRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, procedure_id: int) -> Procedure | None:
        stmt = select(Procedure).where(Procedure.id == procedure_id)
        return self.db.scalar(stmt)

    def list_all(self, skip: int = 0, limit: int = 100, only_active: bool = False) -> list[Procedure]:
        stmt = select(Procedure)
        if only_active:
            stmt = stmt.where(Procedure.is_active.is_(True))
        stmt = stmt.offset(skip).limit(limit)
        return list(self.db.scalars(stmt).all())

    def create(self, procedure_in: ProcedureCreate) -> Procedure:
        procedure = Procedure(**procedure_in.model_dump())
        self.db.add(procedure)
        self.db.commit()
        self.db.refresh(procedure)
        return procedure

    def update(self, procedure: Procedure, procedure_in: ProcedureUpdate) -> Procedure:
        data = procedure_in.model_dump(exclude_unset=True)
        for field, value in data.items():
            setattr(procedure, field, value)
        self.db.add(procedure)
        self.db.commit()
        self.db.refresh(procedure)
        return procedure

    def delete(self, procedure: Procedure) -> None:
        self.db.delete(procedure)
        self.db.commit()