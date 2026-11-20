import httpx
from typing import List, Optional
from app.ai.providers.base import BaseAIProvider, AgentChatMessage, AgentResponse

class OpenAIAdapter(BaseAIProvider):
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model

    async def chat(
        self, 
        system_prompt: str, 
        messages: List[AgentChatMessage], 
        temperature: float = 0.3
    ) -> AgentResponse:
        if not self.api_key:
            return AgentResponse(
                content="OpenAI API key not configured. Please supply OPENAI_API_KEY.",
                tokens_consumed=0
            )

        api_messages = [{"role": "system", "content": system_prompt}]
        for m in messages:
            api_messages.append({"role": m.role, "content": m.content})

        payload = {
            "model": self.model,
            "messages": api_messages,
            "temperature": temperature
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                choice = data["choices"][0]
                content = choice["message"]["content"]
                tokens = data.get("usage", {}).get("total_tokens", 0)
                return AgentResponse(content=content, tokens_consumed=tokens)
            else:
                return AgentResponse(
                    content=f"OpenAI API Error ({resp.status_code}): {resp.text}",
                    tokens_consumed=0
                )
