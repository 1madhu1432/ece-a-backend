from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class AgentChatMessage(BaseModel):
    role: str # system, user, assistant
    content: str

class AgentResponse(BaseModel):
    content: str
    tokens_consumed: int = 0
    code_diff: Optional[str] = None
    suggested_code: Optional[str] = None

class BaseAIProvider(ABC):
    @abstractmethod
    async def chat(
        self, 
        system_prompt: str, 
        messages: List[AgentChatMessage], 
        temperature: float = 0.3,
        model: Optional[str] = None
    ) -> AgentResponse:
        pass
