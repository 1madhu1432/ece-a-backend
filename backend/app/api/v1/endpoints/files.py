from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.project_service import ProjectService
from app.repositories.file_repo import FileRepository
from app.schemas.project import ProjectFileCreate, ProjectFileUpdate, ProjectFileResponse

router = APIRouter()

@router.get("/{project_id}/files", response_model=List[ProjectFileResponse])
async def list_files(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    project_service = ProjectService(db)
    await project_service.get_project(project_id, current_user.id) # auth verification
    file_repo = FileRepository(db)
    files = await file_repo.list_by_project(project_id)
    return [ProjectFileResponse.model_validate(f) for f in files]

@router.post("/{project_id}/files", response_model=ProjectFileResponse, status_code=status.HTTP_201_CREATED)
async def create_file(
    project_id: UUID,
    req: ProjectFileCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    project_service = ProjectService(db)
    await project_service.get_project(project_id, current_user.id)
    file_repo = FileRepository(db)
    file = await file_repo.create_file(
        project_id=project_id,
        name=req.name,
        path=req.path,
        content=req.content,
        is_entrypoint=req.is_entrypoint
    )
    return ProjectFileResponse.model_validate(file)

@router.put("/files/{file_id}", response_model=ProjectFileResponse)
async def update_file(
    file_id: UUID,
    req: ProjectFileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    file_repo = FileRepository(db)
    file = await file_repo.get_by_id(file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    project_service = ProjectService(db)
    await project_service.get_project(file.project_id, current_user.id)

    updated = await file_repo.update_file(file, content=req.content, name=req.name)
    return ProjectFileResponse.model_validate(updated)

@router.delete("/files/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    file_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    file_repo = FileRepository(db)
    file = await file_repo.get_by_id(file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    project_service = ProjectService(db)
    await project_service.get_project(file.project_id, current_user.id)
    await file_repo.delete_file(file)
