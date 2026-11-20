from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class AIChatRequest(BaseModel):
    conversation_id: Optional[UUID] = None
    project_id: Optional[UUID] = None
    prompt: str = Field(..., min_length=1)
    agent_role: str = "ECE Tutor"
    active_code: Optional[str] = None
    selected_code: Optional[str] = None
    last_error: Optional[str] = None

class AIMessageResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    sender: str
    agent_role: str
    content: str
    code_diff: Optional[str] = None
    tokens_consumed: int
    created_at: datetime

    class Config:
        from_attributes = True

class AIConversationResponse(BaseModel):
    id: UUID
    title: str
    project_id: Optional[UUID]
    created_at: datetime
    messages: List[AIMessageResponse] = []

    class Config:
        from_attributes = True
