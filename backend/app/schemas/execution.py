from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

class ExecutionSubmitRequest(BaseModel):
    project_id: UUID
    file_id: Optional[UUID] = None
    code_override: Optional[str] = None
    engine: str = Field(default="octave", pattern="^(octave|matlab)$")

class ExecutionArtifactResponse(BaseModel):
    id: UUID
    artifact_type: str
    storage_key: str
    filename: str
    file_size_bytes: int
    mime_type: str
    download_url: Optional[str] = None

    class Config:
        from_attributes = True

class ExecutionResultResponse(BaseModel):
    stdout: str
    stderr: str
    variables_json: Dict[str, Any] = {}
    error_summary: Optional[str] = None

    class Config:
        from_attributes = True

class ExecutionResponse(BaseModel):
    id: UUID
    project_id: UUID
    file_id: Optional[UUID]
    user_id: UUID
    engine: str
    status: str
    exit_code: Optional[int]
    duration_ms: Optional[int]
    submitted_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    results: Optional[ExecutionResultResponse] = None
    artifacts: List[ExecutionArtifactResponse] = []

    class Config:
        from_attributes = True
