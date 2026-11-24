from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.procedure_session import ProcedureSession
from app.schemas.procedure_session import ProcedureSessionCreate, ProcedureSessionUpdate


class ProcedureSessionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, session_id: int) -> ProcedureSession | None:
        stmt = select(ProcedureSession).where(ProcedureSession.id == session_id)
        return self.db.scalar(stmt)

    def list_by_appointment(self, appointment_id: int) -> list[ProcedureSession]:
        stmt = (
            select(ProcedureSession)
            .where(ProcedureSession.appointment_id == appointment_id)
            .order_by(ProcedureSession.session_number.asc())
        )
        return list(self.db.scalars(stmt).all())

    def create(self, session_in: ProcedureSessionCreate) -> ProcedureSession:
        proc_session = ProcedureSession(**session_in.model_dump())
        self.db.add(proc_session)
        self.db.commit()
        self.db.refresh(proc_session)
        return proc_session

    def update(self, proc_session: ProcedureSession, session_in: ProcedureSessionUpdate) -> ProcedureSession:
        data = session_in.model_dump(exclude_unset=True)
        for field, value in data.items():
            setattr(proc_session, field, value)
        self.db.add(proc_session)
        self.db.commit()
        self.db.refresh(proc_session)
        return proc_session

    def delete(self, proc_session: ProcedureSession) -> None:
        self.db.delete(proc_session)
        self.db.commit()