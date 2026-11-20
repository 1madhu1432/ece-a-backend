from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class ProjectFileCreate(BaseModel):
    name: str = Field(..., min_length=1)
    path: str = Field(..., min_length=1)
    content: str = ""
    is_entrypoint: bool = False

class ProjectFileUpdate(BaseModel):
    name: Optional[str] = None
    content: Optional[str] = None
    is_entrypoint: Optional[bool] = None

class ProjectFileResponse(BaseModel):
    id: UUID
    project_id: UUID
    name: str
    path: str
    content: str
    is_entrypoint: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    default_engine: str = "octave"
    experiment_id: Optional[UUID] = None

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    default_engine: Optional[str] = None
    is_public: Optional[bool] = None

class ProjectResponse(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    description: Optional[str]
    default_engine: str
    is_public: bool
    created_at: datetime
    updated_at: datetime
    files: List[ProjectFileResponse] = []

    class Config:
        from_attributes = True
