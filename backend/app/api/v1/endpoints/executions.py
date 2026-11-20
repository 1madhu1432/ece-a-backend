from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
import os
import shutil
from pathlib import Path
from app.core.database import get_db
from app.core.config import settings
from app.api.deps import get_current_user
from app.models.user import User
from app.repositories.project_repo import ProjectRepository
from app.repositories.file_repo import FileRepository
from app.repositories.execution_repo import ExecutionRepository
from app.schemas.execution import ExecutionSubmitRequest, ExecutionResponse, ExecutionResultResponse, ExecutionArtifactResponse
from execution_worker.runners.python_runner import PythonRunner
from execution_worker.runners.octave_runner import OctaveRunner

router = APIRouter()

@router.post("/run", response_model=ExecutionResponse)
async def run_code(
    req: ExecutionSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    project_repo = ProjectRepository(db)
    file_repo = FileRepository(db)
    exec_repo = ExecutionRepository(db)

    project = await project_repo.get_by_id(req.project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied or project not found.")

    code_to_run = req.code_override
    if not code_to_run and req.file_id:
        file = await file_repo.get_by_id(req.file_id)
        if file:
            code_to_run = file.content

    if not code_to_run:
        raise HTTPException(status_code=400, detail="No source code provided to execute.")

    # 1. Create execution record
    execution = await exec_repo.create_execution(
        user_id=current_user.id,
        project_id=project.id,
        file_id=req.file_id,
        engine=req.engine
    )

    # 2. Execute via selected runner
    if req.engine == "python":
        runner = PythonRunner()
    else:
        runner = OctaveRunner()

    result = await runner.execute(code_to_run, timeout_seconds=15)

    status_str = "completed" if result.exit_code == 0 else "failed"
    if result.error == "TIMEOUT":
        status_str = "timeout"

    # 3. Save Execution Result
    await exec_repo.save_results(
        execution=execution,
        status=status_str,
        exit_code=result.exit_code,
        duration_ms=result.duration_ms,
        stdout=result.stdout,
        stderr=result.stderr,
        variables_json=result.variables,
        error_summary=result.error
    )

    # 4. Save Artifacts (Figures)
    artifacts_resp = []
    for fig in result.figures:
        fig_idx = fig["fig_index"]
        if fig.get("png_path") and os.path.exists(fig["png_path"]):
            orig_filename = fig.get("filename") or f"Figure_{fig_idx}.png"
            clean_name = os.path.basename(orig_filename)
            dest_filename = f"{execution.id}_{clean_name}"
            dest_path = os.path.join(settings.STORAGE_DIR, "artifacts", dest_filename)
            shutil.copyfile(fig["png_path"], dest_path)
            file_size = os.path.getsize(dest_path)

            art = await exec_repo.add_artifact(
                execution_id=execution.id,
                artifact_type="figure_png",
                storage_key=dest_filename,
                filename=clean_name,
                file_size_bytes=file_size,
                mime_type="image/png"
            )
            artifacts_resp.append(ExecutionArtifactResponse(
                id=art.id,
                artifact_type="figure_png",
                storage_key=art.storage_key,
                filename=art.filename,
                file_size_bytes=art.file_size_bytes,
                mime_type=art.mime_type,
                download_url=f"/api/v1/storage/artifacts/{dest_filename}"
            ))

    # Clean temporary execution sandbox after copying artifacts
    if result.run_dir and os.path.exists(result.run_dir):
        shutil.rmtree(result.run_dir, ignore_errors=True)

    return ExecutionResponse(
        id=execution.id,
        project_id=execution.project_id,
        file_id=execution.file_id,
        user_id=execution.user_id,
        engine=execution.engine,
        status=execution.status,
        exit_code=execution.exit_code,
        duration_ms=execution.duration_ms,
        submitted_at=execution.submitted_at,
        started_at=execution.started_at,
        completed_at=execution.completed_at,
        results=ExecutionResultResponse(
            stdout=result.stdout,
            stderr=result.stderr,
            variables_json=result.variables,
            error_summary=result.error
        ),
        artifacts=artifacts_resp
    )

@router.get("/project/{project_id}", response_model=List[ExecutionResponse])
async def list_project_executions(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    project_repo = ProjectRepository(db)
    project = await project_repo.get_by_id(project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied.")

    exec_repo = ExecutionRepository(db)
    executions = await exec_repo.list_by_project(project_id)
    return [ExecutionResponse.model_validate(e) for e in executions]
