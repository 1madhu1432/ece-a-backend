from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime

class ReportGenerateRequest(BaseModel):
    project_id: UUID
    execution_id: Optional[UUID] = None
    title: str = Field(..., min_length=2)
    student_name: str
    roll_number: Optional[str] = None
    semester: Optional[str] = "5th Sem"
    additional_notes: Optional[str] = None

class GeneratedReportResponse(BaseModel):
    id: UUID
    project_id: UUID
    execution_id: Optional[UUID]
    title: str
    pdf_storage_key: str
    download_url: Optional[str] = None
    sections_json: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True
