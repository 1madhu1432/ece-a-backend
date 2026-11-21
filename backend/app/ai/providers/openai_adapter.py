import httpx
from typing import List, Optional
from app.ai.providers.base import BaseAIProvider, AgentChatMessage, AgentResponse
from app.ai.knowledge_engine import ECEKnowledgeEngine

class OpenAIAdapter(BaseAIProvider):
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model

    async def chat(
        self, 
        system_prompt: str, 
        messages: List[AgentChatMessage], 
        temperature: float = 0.3,
        model: Optional[str] = None
    ) -> AgentResponse:
        active_model = model or self.model
        last_user_msg = messages[-1].content if messages else ""

        if not self.api_key:
            return ECEKnowledgeEngine.synthesize_response(
                prompt=last_user_msg,
                history=messages
            )

        api_messages = [{"role": "system", "content": system_prompt}]
        for m in messages:
            api_messages.append({"role": m.role, "content": m.content})

        payload = {
            "model": active_model,
            "messages": api_messages,
            "temperature": temperature
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    choice = data["choices"][0]
                    content = choice["message"]["content"]
                    tokens = data.get("usage", {}).get("total_tokens", 0)
                    suggested_code = ECEKnowledgeEngine.extract_code_snippet(content)
                    return AgentResponse(content=content, tokens_consumed=tokens, suggested_code=suggested_code)
                else:
                    fallback_resp = ECEKnowledgeEngine.synthesize_response(prompt=last_user_msg, history=messages)
                    fallback_resp.content = f"> [Note: OpenAI API returned {resp.status_code}; falling back to ECE Studio Intelligence Engine]\n\n" + fallback_resp.content
                    return fallback_resp
        except Exception:
            fallback_resp = ECEKnowledgeEngine.synthesize_response(prompt=last_user_msg, history=messages)
            fallback_resp.content = "> [Note: OpenAI API connection timed out; using ECE Studio Intelligence Engine]\n\n" + fallback_resp.content
            return fallback_resp
