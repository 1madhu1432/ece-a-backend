from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID
from app.models.project import ProjectFile

class FileRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_by_project(self, project_id: UUID) -> List[ProjectFile]:
        stmt = select(ProjectFile).where(ProjectFile.project_id == project_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, file_id: UUID) -> Optional[ProjectFile]:
        stmt = select(ProjectFile).where(ProjectFile.id == file_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_file(
        self, 
        project_id: UUID, 
        name: str, 
        path: str, 
        content: str = "", 
        is_entrypoint: bool = False
    ) -> ProjectFile:
        file = ProjectFile(
            project_id=project_id,
            name=name,
            path=path,
            content=content,
            is_entrypoint=is_entrypoint
        )
        self.db.add(file)
        await self.db.commit()
        await self.db.refresh(file)
        return file

    async def update_file(self, file: ProjectFile, content: Optional[str] = None, name: Optional[str] = None) -> ProjectFile:
        if content is not None:
            file.content = content
        if name is not None:
            file.name = name
        await self.db.commit()
        await self.db.refresh(file)
        return file

    async def delete_file(self, file: ProjectFile) -> None:
        await self.db.delete(file)
        await self.db.commit()
