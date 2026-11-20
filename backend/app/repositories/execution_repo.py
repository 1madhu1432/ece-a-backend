from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional
from uuid import UUID
from app.models.execution import Execution, ExecutionResult, ExecutionArtifact

class ExecutionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_execution(
        self, 
        user_id: UUID, 
        project_id: UUID, 
        file_id: Optional[UUID], 
        engine: str
    ) -> Execution:
        execution = Execution(
            user_id=user_id,
            project_id=project_id,
            file_id=file_id,
            engine=engine,
            status="queued"
        )
        self.db.add(execution)
        await self.db.commit()
        await self.db.refresh(execution)
        return execution

    async def get_by_id(self, execution_id: UUID) -> Optional[Execution]:
        stmt = select(Execution).where(Execution.id == execution_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_project(self, project_id: UUID, limit: int = 20) -> List[Execution]:
        stmt = (
            select(Execution)
            .where(Execution.project_id == project_id)
            .order_by(desc(Execution.submitted_at))
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def save_results(
        self, 
        execution: Execution, 
        status: str, 
        exit_code: int, 
        duration_ms: int, 
        stdout: str, 
        stderr: str, 
        variables_json: dict,
        error_summary: Optional[str] = None
    ) -> Execution:
        execution.status = status
        execution.exit_code = exit_code
        execution.duration_ms = duration_ms

        result = ExecutionResult(
            execution_id=execution.id,
            stdout=stdout,
            stderr=stderr,
            variables_json=variables_json,
            error_summary=error_summary
        )
        self.db.add(result)
        await self.db.commit()
        await self.db.refresh(execution)
        return execution

    async def add_artifact(
        self,
        execution_id: UUID,
        artifact_type: str,
        storage_key: str,
        filename: str,
        file_size_bytes: int,
        mime_type: str
    ) -> ExecutionArtifact:
        artifact = ExecutionArtifact(
            execution_id=execution_id,
            artifact_type=artifact_type,
            storage_key=storage_key,
            filename=filename,
            file_size_bytes=file_size_bytes,
            mime_type=mime_type
        )
        self.db.add(artifact)
        await self.db.commit()
        await self.db.refresh(artifact)
        return artifact
