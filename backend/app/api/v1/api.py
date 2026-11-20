from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    users,
    projects,
    files,
    executions,
    experiments,
    ai,
    reports,
    admin
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(files.router, prefix="/projects", tags=["Project Files"])
api_router.include_router(executions.router, prefix="/executions", tags=["Executions"])
api_router.include_router(experiments.router, prefix="/experiments", tags=["Experiments"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI Assistant"])
api_router.include_router(reports.router, prefix="/reports", tags=["Lab Reports"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin Panel"])
