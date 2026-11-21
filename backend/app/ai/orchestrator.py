from typing import List, Optional
from app.core.config import settings
from app.ai.providers.base import BaseAIProvider, AgentChatMessage, AgentResponse
from app.ai.providers.gemini_adapter import GeminiAdapter
from app.ai.providers.openai_adapter import OpenAIAdapter
from app.ai.agents.specialized import AGENT_PROMPTS
from app.ai.knowledge_engine import ECEKnowledgeEngine

class AIOrchestrator:
    def __init__(self):
        self.gemini_provider = GeminiAdapter(api_key=settings.GEMINI_API_KEY)
        self.openai_provider = OpenAIAdapter(api_key=settings.OPENAI_API_KEY)

    def get_provider(self, provider_name: Optional[str] = None) -> BaseAIProvider:
        chosen = provider_name or settings.AI_DEFAULT_PROVIDER
        if chosen == "openai":
            return self.openai_provider
        return self.gemini_provider

    async def process_chat(
        self,
        prompt: str,
        agent_role: str = "ECE Tutor",
        subject: Optional[str] = None,
        language: str = "octave",
        conversation_history: Optional[List[AgentChatMessage]] = None,
        active_code: Optional[str] = None,
        selected_code: Optional[str] = None,
        last_error: Optional[str] = None,
        execution_output: Optional[str] = None,
        experiment_title: Optional[str] = None,
        experiment_theory: Optional[str] = None,
        graph_metadata: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None
    ) -> AgentResponse:
        # 1. Determine Base Role & Subject Guidance
        role_key = subject if (subject and subject in AGENT_PROMPTS) else agent_role
        base_prompt = AGENT_PROMPTS.get(role_key, AGENT_PROMPTS["ECE Tutor"])

        # 2. Strict Prompt-Injection Guardrails & Output Formatting Requirements
        guardrails = (
            "\n[ENGINEERING PEDAGOGY & SAFETY GUIDELINES]:\n"
            "- You are assisting an undergraduate B.Tech Electronics and Communication Engineering student.\n"
            "- Provide mathematically sound, physically intuitive explanations.\n"
            "- When writing equations, always use LaTeX notation (e.g. $f_s \\ge 2 f_{max}$, $y[n] = x[n] * h[n]$).\n"
            "- When generating code, provide fully standalone, executable code blocks with sample figures/plots.\n"
            "- Never execute code automatically; generated code must be user-reviewed and manually run in Studio.\n"
            "- Stay strictly within the scope of engineering, scientific computing, mathematics, and academic ECE curriculum.\n"
        )

        context_parts = [base_prompt, guardrails]
        context_parts.append(f"Active IDE Programming Language: {language.upper()}")

        # 3. Context Ingestion with Length Bounds
        if active_code:
            context_parts.append(f"\n--- ACTIVE FILE SOURCE CODE ({language.upper()}) ---\n{active_code[:3500]}\n--- END ACTIVE CODE ---")
        if selected_code:
            context_parts.append(f"\n--- STUDENT SELECTED CODE REGION ---\n{selected_code[:1200]}\n--- END SELECTION ---")
        if last_error:
            context_parts.append(f"\n--- LATEST RUNTIME ERROR / TRACEBACK ---\n{last_error[:1500]}\n--- END ERROR TRACEBACK ---")
        if execution_output:
            context_parts.append(f"\n--- RECENT CONSOLE OUTPUT ---\n{execution_output[:1200]}\n--- END CONSOLE OUTPUT ---")
        if experiment_title:
            context_parts.append(f"\n--- LINKED EXPERIMENT CURRICULUM ---\nTitle: {experiment_title}")
            if experiment_theory:
                context_parts.append(f"Theory: {experiment_theory[:1000]}")
            context_parts.append("--- END CURRICULUM ---")
        if graph_metadata:
            context_parts.append(f"\n--- GENERATED SIMULATION GRAPH METADATA ---\n{graph_metadata[:800]}\n--- END GRAPH METADATA ---")

        system_instruction = "\n".join(context_parts)

        # 4. Check if external provider API key exists
        active_provider = self.get_provider(provider)
        is_provider_configured = (
            (isinstance(active_provider, OpenAIAdapter) and settings.OPENAI_API_KEY) or
            (isinstance(active_provider, GeminiAdapter) and settings.GEMINI_API_KEY)
        )

        if not is_provider_configured:
            # Delegate directly to our ECE Knowledge Engine for instant, reliable responses
            resp = ECEKnowledgeEngine.synthesize_response(
                prompt=prompt,
                agent_role=agent_role,
                subject=subject,
                language=language,
                active_code=active_code,
                selected_code=selected_code,
                last_error=last_error,
                execution_output=execution_output,
                experiment_title=experiment_title,
                experiment_theory=experiment_theory,
                graph_metadata=graph_metadata,
                history=conversation_history
            )
            return resp

        # 5. Execute via Live Provider API with History
        messages = list(conversation_history or [])
        messages.append(AgentChatMessage(role="user", content=prompt))

        try:
            resp = await active_provider.chat(
                system_prompt=system_instruction,
                messages=messages,
                model=model
            )
            # If the provider failed or returned an error status message, fallback with full context!
            if not resp or (resp.content and resp.content.startswith("> [Note:")):
                return ECEKnowledgeEngine.synthesize_response(
                    prompt=prompt,
                    agent_role=agent_role,
                    subject=subject,
                    language=language,
                    active_code=active_code,
                    selected_code=selected_code,
                    last_error=last_error,
                    execution_output=execution_output,
                    experiment_title=experiment_title,
                    experiment_theory=experiment_theory,
                    graph_metadata=graph_metadata,
                    history=conversation_history
                )
        except Exception:
            return ECEKnowledgeEngine.synthesize_response(
                prompt=prompt,
                agent_role=agent_role,
                subject=subject,
                language=language,
                active_code=active_code,
                selected_code=selected_code,
                last_error=last_error,
                execution_output=execution_output,
                experiment_title=experiment_title,
                experiment_theory=experiment_theory,
                graph_metadata=graph_metadata,
                history=conversation_history
            )

        # Ensure suggested_code is extracted if LLM response contained code blocks
        if not resp.suggested_code:
            resp.suggested_code = ECEKnowledgeEngine.extract_code_snippet(resp.content)

        return resp
