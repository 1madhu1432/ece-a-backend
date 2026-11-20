import httpx
from typing import List, Optional
from app.ai.providers.base import BaseAIProvider, AgentChatMessage, AgentResponse

class GeminiAdapter(BaseAIProvider):
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model = model

    async def chat(
        self, 
        system_prompt: str, 
        messages: List[AgentChatMessage], 
        temperature: float = 0.3
    ) -> AgentResponse:
        if not self.api_key:
            # High-fidelity domain-aware rule-based fallback response for development/demo
            last_user_msg = messages[-1].content if messages else ""
            fallback_text = (
                f"### Analysis by ECE AI Studio\n\n"
                f"I have reviewed your query:\n> {last_user_msg}\n\n"
                f"**Key Engineering Insight:**\n"
                f"In Digital Signal Processing and Communications, ensure your sampling rate $f_s$ satisfies the Nyquist-Shannon criterion ($f_s \\ge 2 f_{max}$) to avoid aliasing distortion.\n\n"
                f"**Recommended Code:**\n"
                f"```octave\n"
                f"fs = 1000;           % Sampling rate 1 kHz\n"
                f"t = 0:1/fs:1-1/fs;   % 1 second duration\n"
                f"f0 = 50;             % 50 Hz carrier\n"
                f"x = sin(2*pi*f0*t);  % Generated waveform\n"
                f"figure(1); plot(t(1:100), x(1:100)); grid on;\n"
                f"title('Synthesized Signal Waveform');\n"
                f"xlabel('Time (s)'); ylabel('Amplitude');\n"
                f"```\n\n"
                f"*To enable live Gemini API completions, configure GEMINI_API_KEY in your environment.*"
            )
            return AgentResponse(content=fallback_text, tokens_consumed=150)

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        
        contents = []
        contents.append({"role": "user", "parts": [{"text": f"System Instructions: {system_prompt}"}]})
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

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                candidate = data.get("candidates", [{}])[0]
                text = candidate.get("content", {}).get("parts", [{}])[0].get("text", "")
                tokens = data.get("usageMetadata", {}).get("totalTokenCount", 0)
                return AgentResponse(content=text, tokens_consumed=tokens)
            else:
                return AgentResponse(
                    content=f"Gemini API Error ({resp.status_code}): {resp.text}",
                    tokens_consumed=0
                )
