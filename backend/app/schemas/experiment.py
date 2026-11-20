from pydantic import BaseModel
from typing import Optional, List, Any
from uuid import UUID
from datetime import datetime

class ExperimentCategoryResponse(BaseModel):
    id: UUID
    name: str
    code: str
    description: Optional[str]
    display_order: int

    class Config:
        from_attributes = True

class ExperimentSummaryResponse(BaseModel):
    id: UUID
    category_id: UUID
    title: str
    slug: str
    engine: str
    objective: str

    class Config:
        from_attributes = True

class ExperimentDetailResponse(BaseModel):
    id: UUID
    category_id: UUID
    title: str
    slug: str
    objective: str
    theory: str
    equations_json: List[Any]
    procedure_json: List[Any]
    default_code: str
    engine: str
    expected_output: Optional[str]

    class Config:
        from_attributes = True
