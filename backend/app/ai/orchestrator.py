from typing import List, Optional
from app.core.config import settings
from app.ai.providers.base import BaseAIProvider, AgentChatMessage, AgentResponse
from app.ai.providers.gemini_adapter import GeminiAdapter
from app.ai.providers.openai_adapter import OpenAIAdapter
from app.ai.agents.specialized import AGENT_PROMPTS

class AIOrchestrator:
    def __init__(self):
        # Choose provider based on config
        if settings.AI_DEFAULT_PROVIDER == "openai" and settings.OPENAI_API_KEY:
            self.provider: BaseAIProvider = OpenAIAdapter(api_key=settings.OPENAI_API_KEY)
        else:
            self.provider = GeminiAdapter(api_key=settings.GEMINI_API_KEY)

    async def process_chat(
        self,
        prompt: str,
        agent_role: str = "ECE Tutor",
        conversation_history: Optional[List[AgentChatMessage]] = None,
        active_code: Optional[str] = None,
        selected_code: Optional[str] = None,
        last_error: Optional[str] = None
    ) -> AgentResponse:
        base_prompt = AGENT_PROMPTS.get(agent_role, AGENT_PROMPTS["ECE Tutor"])

        # Context Injection
        context_parts = [base_prompt]
        if active_code:
            context_parts.append(f"\n--- CURRENT ACTIVE FILE CODE ---\n{active_code[:3000]}\n--- END CODE ---")
        if selected_code:
            context_parts.append(f"\n--- STUDENT SELECTED CODE ---\n{selected_code[:1000]}\n--- END SELECTED ---")
        if last_error:
            context_parts.append(f"\n--- RECENT EXECUTION ERROR TRACEBACK ---\n{last_error[:1500]}\n--- END ERROR ---")

        system_instruction = "\n".join(context_parts)

        messages = list(conversation_history or [])
        messages.append(AgentChatMessage(role="user", content=prompt))

        return await self.provider.chat(system_prompt=system_instruction, messages=messages)
