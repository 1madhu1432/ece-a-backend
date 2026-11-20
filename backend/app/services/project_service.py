from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from typing import List, Optional
from uuid import UUID
from app.repositories.project_repo import ProjectRepository
from app.repositories.file_repo import FileRepository
from app.models.project import Project, ProjectFile

class ProjectService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.project_repo = ProjectRepository(db)
        self.file_repo = FileRepository(db)

    async def list_user_projects(self, user_id: UUID) -> List[Project]:
        return await self.project_repo.list_by_user(user_id)

    async def get_project(self, project_id: UUID, user_id: UUID) -> Project:
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
        if project.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
        return project

    async def create_project(
        self, 
        user_id: UUID, 
        name: str, 
        description: Optional[str] = None, 
        default_engine: str = "octave",
        experiment_id: Optional[UUID] = None
    ) -> Project:
        return await self.project_repo.create_project(
            user_id=user_id,
            name=name,
            description=description,
            default_engine=default_engine,
            experiment_id=experiment_id
        )

    async def update_project(
        self, 
        project_id: UUID, 
        user_id: UUID, 
        name: Optional[str] = None, 
        description: Optional[str] = None,
        default_engine: Optional[str] = None
    ) -> Project:
        project = await self.get_project(project_id, user_id)
        if name:
            project.name = name
        if description is not None:
            project.description = description
        if default_engine:
            project.default_engine = default_engine
        return await self.project_repo.update_project(project)

    async def delete_project(self, project_id: UUID, user_id: UUID) -> None:
        project = await self.get_project(project_id, user_id)
        await self.project_repo.delete_project(project)
