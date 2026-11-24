from fastapi import FastAPI

from app.api.routers.appointments import router as appointments_router
from app.api.routers.auth import router as auth_router
from app.api.routers.client_profiles import router as client_profiles_router
from app.api.routers.employee_profiles import router as employee_profiles_router
from app.api.routers.procedure_sessions import router as procedure_sessions_router
from app.api.routers.procedures import router as procedures_router
from app.api.routers.users import router as users_router

app = FastAPI(title="Harmony Spa API")

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(client_profiles_router)
app.include_router(employee_profiles_router)
app.include_router(procedures_router)
app.include_router(appointments_router)
app.include_router(procedure_sessions_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}