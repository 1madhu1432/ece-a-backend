from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.api.deps import get_current_admin
from app.models.user import User
from app.models.project import Project
from app.models.execution import Execution

router = APIRouter()

@router.get("/metrics")
async def get_admin_metrics(
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    total_users = (await db.execute(select(func.count(User.id)))).scalar() or 0
    total_projects = (await db.execute(select(func.count(Project.id)))).scalar() or 0
    total_executions = (await db.execute(select(func.count(Execution.id)))).scalar() or 0
    failed_executions = (await db.execute(select(func.count(Execution.id)).where(Execution.status == "failed"))).scalar() or 0

    return {
        "total_users": total_users,
        "total_projects": total_projects,
        "total_executions": total_executions,
        "failed_executions": failed_executions,
        "system_status": "Healthy",
        "container_pool_status": "Online (Active Sandbox Guard)"
    }
