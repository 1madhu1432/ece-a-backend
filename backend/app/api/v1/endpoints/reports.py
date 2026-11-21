from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List
from uuid import UUID
import os
from app.core.database import get_db
from app.core.config import settings
from app.api.deps import get_current_user
from app.models.user import User, UserProfile
from app.models.project import Project, ProjectFile
from app.models.execution import Execution, ExecutionResult, ExecutionArtifact
from app.models.experiment import Experiment
from app.models.report import GeneratedReport
from app.schemas.report import ReportGenerateRequest, GeneratedReportResponse
from app.services.report_service import ReportGenerator

router = APIRouter()

@router.post("/generate", response_model=GeneratedReportResponse, status_code=status.HTTP_201_CREATED)
async def generate_report(
    req: ReportGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    proj_res = await db.execute(select(Project).where(Project.id == req.project_id))
    project = proj_res.scalar_one_or_none()
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Project not found or unauthorized.")

    prof_res = await db.execute(select(UserProfile).where(UserProfile.user_id == current_user.id))
    profile = prof_res.scalar_one_or_none()
    college = profile.college_name if profile else "Department of ECE"

    # Fetch execution details if provided
    exec_output = ""
    source_code = ""
    figures = []
    if req.execution_id:
        exec_res = await db.execute(select(Execution).where(Execution.id == req.execution_id))
        execution = exec_res.scalar_one_or_none()
        if execution:
            res_stmt = select(ExecutionResult).where(ExecutionResult.execution_id == execution.id)
            result = (await db.execute(res_stmt)).scalar_one_or_none()
            if result:
                exec_output = result.stdout + ("\n" + result.stderr if result.stderr else "")

            # Load any PNG figure artifacts generated in this execution for the PDF report
            art_stmt = select(ExecutionArtifact).where(ExecutionArtifact.execution_id == execution.id)
            artifacts = (await db.execute(art_stmt)).scalars().all()
            for art in artifacts:
                if art.filename.lower().endswith((".png", ".jpg", ".jpeg")) or art.artifact_type == "figure_png":
                    fig_path = os.path.join(settings.STORAGE_DIR, "artifacts", art.storage_key)
                    if os.path.exists(fig_path) and fig_path not in figures:
                        figures.append(fig_path)

            if execution.file_id:
                file_res = await db.execute(select(ProjectFile).where(ProjectFile.id == execution.file_id))
                target_file = file_res.scalar_one_or_none()
                if target_file:
                    source_code = target_file.content

    if not source_code and project.files:
        source_code = project.files[0].content

    # Determine real experiment metadata if linked
    report_objective = project.description or f"Design, simulation and analysis of {req.title}."
    report_theory = "The mathematical formulations and theoretical governing principles are simulated in this project."
    if project.experiment_id:
        exp_res = await db.execute(select(Experiment).where(Experiment.id == project.experiment_id))
        linked_exp = exp_res.scalar_one_or_none()
        if linked_exp:
            report_objective = linked_exp.objective or report_objective
            report_theory = linked_exp.theory or report_theory

    # Output file path
    report_filename = f"report_{project.id}_{int(os.times().system)}.pdf"
    output_filepath = os.path.join(settings.STORAGE_DIR, "reports", report_filename)

    ReportGenerator.create_lab_report(
        output_filepath=output_filepath,
        student_name=req.student_name,
        college_name=college,
        roll_number=req.roll_number or "ECE-2024",
        experiment_title=req.title,
        objective=report_objective,
        theory=report_theory,
        source_code=source_code,
        execution_output=exec_output,
        figures=figures
    )

    report = GeneratedReport(
        project_id=project.id,
        execution_id=req.execution_id,
        user_id=current_user.id,
        title=req.title,
        pdf_storage_key=report_filename,
        sections_json={
            "student_name": req.student_name,
            "roll_number": req.roll_number,
            "college": college
        }
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)

    return GeneratedReportResponse(
        id=report.id,
        project_id=report.project_id,
        execution_id=report.execution_id,
        title=report.title,
        pdf_storage_key=report.pdf_storage_key,
        download_url=f"/api/v1/reports/{report.id}/download",
        sections_json=report.sections_json,
        created_at=report.created_at
    )

@router.get("/{report_id}/download")
async def download_report(
    report_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    rep_res = await db.execute(select(GeneratedReport).where(GeneratedReport.id == report_id))
    report = rep_res.scalar_one_or_none()
    if not report or report.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Report not found or unauthorized.")

    filepath = os.path.join(settings.STORAGE_DIR, "reports", report.pdf_storage_key)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Report file not found on server.")

    return FileResponse(filepath, media_type="application/pdf", filename=f"{report.title}.pdf")

@router.get("", response_model=List[GeneratedReportResponse])
async def list_reports(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(GeneratedReport).where(GeneratedReport.user_id == current_user.id).order_by(desc(GeneratedReport.created_at))
    res = await db.execute(stmt)
    reports = list(res.scalars().all())
    return [
        GeneratedReportResponse(
            id=r.id,
            project_id=r.project_id,
            execution_id=r.execution_id,
            title=r.title,
            pdf_storage_key=r.pdf_storage_key,
            download_url=f"/api/v1/reports/{r.id}/download",
            sections_json=r.sections_json,
            created_at=r.created_at
        )
        for r in reports
    ]
