from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.repositories.experiment_repo import ExperimentRepository
from app.repositories.project_repo import ProjectRepository
from app.repositories.file_repo import FileRepository
from app.schemas.experiment import ExperimentCategoryResponse, ExperimentSummaryResponse, ExperimentDetailResponse
from app.schemas.project import ProjectResponse

router = APIRouter()

@router.get("/categories", response_model=List[ExperimentCategoryResponse])
async def list_categories(db: AsyncSession = Depends(get_db)):
    repo = ExperimentRepository(db)
    categories = await repo.list_categories()
    return [ExperimentCategoryResponse.model_validate(c) for c in categories]

@router.get("", response_model=List[ExperimentSummaryResponse])
async def list_experiments(category_id: Optional[UUID] = None, db: AsyncSession = Depends(get_db)):
    repo = ExperimentRepository(db)
    experiments = await repo.list_experiments(category_id)
    return [ExperimentSummaryResponse.model_validate(e) for e in experiments]

@router.get("/{slug}", response_model=ExperimentDetailResponse)
async def get_experiment_by_slug(slug: str, db: AsyncSession = Depends(get_db)):
    repo = ExperimentRepository(db)
    exp = await repo.get_by_slug(slug)
    if not exp:
        try:
            exp_uuid = UUID(slug)
            exp = await repo.get_by_id(exp_uuid)
        except ValueError:
            pass
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found.")
    return ExperimentDetailResponse.model_validate(exp)

@router.post("/{slug}/clone", response_model=ProjectResponse)
async def clone_experiment_to_project(
    slug: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    exp_repo = ExperimentRepository(db)
    exp = await exp_repo.get_by_slug(slug)
    if not exp:
        try:
            exp_uuid = UUID(slug)
            exp = await exp_repo.get_by_id(exp_uuid)
        except ValueError:
            pass
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found.")

    proj_repo = ProjectRepository(db)
    file_repo = FileRepository(db)

    project = await proj_repo.create_project(
        user_id=current_user.id,
        name=f"Lab: {exp.title}",
        description=f"Cloned from ECE Experiment Library: {exp.objective}",
        default_engine="octave",
        experiment_id=exp.id
    )

    # Overwrite default entrypoint with verified MATLAB experiment code
    files = await file_repo.list_by_project(project.id)
    if files:
        entry = files[0]
        code_to_use = exp.matlab_code or exp.default_code
        await file_repo.update_file(entry, content=code_to_use)

    await db.refresh(project, ["files"])
    return ProjectResponse.model_validate(project)
