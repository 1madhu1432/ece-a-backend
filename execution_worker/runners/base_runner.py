from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class ExecutionResultPayload(BaseModel):
    stdout: str
    stderr: str
    exit_code: int
    duration_ms: int
    figures: List[Dict[str, Any]] = [] # [{ "type": "svg", "path": "...", "data": ... }]
    variables: Dict[str, Any] = {} # { "varName": { "type": "matrix", "size": "1x100", "preview": "..." } }
    error: Optional[str] = None
    run_dir: Optional[str] = None

class BaseRunner(ABC):
    @abstractmethod
    async def execute(self, code: str, timeout_seconds: int = 15) -> ExecutionResultPayload:
        pass
