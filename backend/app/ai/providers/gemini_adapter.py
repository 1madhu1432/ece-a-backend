import httpx
from typing import List, Optional
from app.ai.providers.base import BaseAIProvider, AgentChatMessage, AgentResponse
from app.ai.knowledge_engine import ECEKnowledgeEngine

class GeminiAdapter(BaseAIProvider):
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-flash"):
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

        # Fallback to local ECE Knowledge Engine if API key is not configured
        if not self.api_key:
            resp = ECEKnowledgeEngine.synthesize_response(
                prompt=last_user_msg,
                history=messages
            )
            return resp

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{active_model}:generateContent?key={self.api_key}"
        
        contents = []
        contents.append({"role": "user", "parts": [{"text": f"System Instructions:\n{system_prompt}"}]})
        for m in messages:
            role = "user" if m.role == "user" else "model"
            contents.append({"role": role, "parts": [{"text": m.content}]})

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": 2048
            }
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    candidate = data.get("candidates", [{}])[0]
                    text = candidate.get("content", {}).get("parts", [{}])[0].get("text", "")
                    tokens = data.get("usageMetadata", {}).get("totalTokenCount", 0)
                    suggested_code = ECEKnowledgeEngine.extract_code_snippet(text)
                    return AgentResponse(content=text, tokens_consumed=tokens, suggested_code=suggested_code)
                else:
                    # On provider error (e.g. quota or bad key), fallback to ECE Knowledge Engine gracefully
                    fallback_resp = ECEKnowledgeEngine.synthesize_response(prompt=last_user_msg, history=messages)
                    fallback_resp.content = f"> [Note: Live Gemini API returned {resp.status_code}; falling back to ECE Studio Intelligence Engine]\n\n" + fallback_resp.content
                    return fallback_resp
        except Exception:
            # On connection or timeout failure, fallback to ECE Knowledge Engine
            fallback_resp = ECEKnowledgeEngine.synthesize_response(prompt=last_user_msg, history=messages)
            fallback_resp.content = "> [Note: Gemini API connection timed out; using ECE Studio Intelligence Engine]\n\n" + fallback_resp.content
            return fallback_resp
