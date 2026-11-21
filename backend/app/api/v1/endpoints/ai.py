from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from typing import List, Optional
from uuid import UUID
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.ai import AIConversation, AIMessage
from app.schemas.ai import AIChatRequest, AIMessageResponse, AIConversationResponse
from app.ai.orchestrator import AIOrchestrator
from app.ai.providers.base import AgentChatMessage

router = APIRouter()
orchestrator = AIOrchestrator()

@router.post("/chat", response_model=AIMessageResponse)
async def ai_chat(
    req: AIChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 1. Enforce Token Usage Quota & Rate Limiting (Students only, non-admin)
    if current_user.role != "admin" and current_user.subscription:
        sub = current_user.subscription
        token_stmt = (
            select(func.coalesce(func.sum(AIMessage.tokens_consumed), 0))
            .join(AIConversation, AIConversation.id == AIMessage.conversation_id)
            .where(AIConversation.user_id == current_user.id)
        )
        total_used = (await db.execute(token_stmt)).scalar_one()
        if total_used >= sub.monthly_ai_token_quota:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Monthly AI token quota ({sub.monthly_ai_token_quota:,} tokens) exceeded. Upgrade your subscription or await quota reset."
            )

    # 2. Find or create conversation
    conv_id = req.conversation_id
    if not conv_id:
        conversation = AIConversation(
            user_id=current_user.id,
            project_id=req.project_id,
            title=req.prompt[:40] + ("..." if len(req.prompt) > 40 else "")
        )
        db.add(conversation)
        await db.flush()
        conv_id = conversation.id
    else:
        conv_res = await db.execute(select(AIConversation).where(AIConversation.id == conv_id))
        conversation = conv_res.scalar_one_or_none()
        if not conversation or conversation.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied to conversation.")

    # 3. Record User Message
    user_msg = AIMessage(
        conversation_id=conv_id,
        sender="user",
        agent_role=req.agent_role,
        content=req.prompt,
        tokens_consumed=0
    )
    db.add(user_msg)
    await db.flush()

    # 4. Retrieve recent history
    history_res = await db.execute(
        select(AIMessage)
        .where(AIMessage.conversation_id == conv_id)
        .order_by(AIMessage.created_at)
    )
    raw_history = list(history_res.scalars().all())
    chat_history = [
        AgentChatMessage(role="user" if m.sender == "user" else "assistant", content=m.content)
        for m in raw_history[-6:]
    ]

    # 5. Invoke Multi-Agent Context-Aware Orchestrator
    ai_resp = await orchestrator.process_chat(
        prompt=req.prompt,
        agent_role=req.agent_role,
        subject=req.subject,
        language=req.language or "octave",
        conversation_history=chat_history,
        active_code=req.active_code,
        selected_code=req.selected_code,
        last_error=req.last_error,
        execution_output=req.execution_output,
        experiment_title=req.experiment_title,
        experiment_theory=req.experiment_theory,
        graph_metadata=req.graph_metadata,
        provider=req.provider,
        model=req.model
    )

    # 6. Record Assistant Message with Suggested Code
    assistant_msg = AIMessage(
        conversation_id=conv_id,
        sender="assistant",
        agent_role=req.agent_role,
        content=ai_resp.content,
        code_diff=ai_resp.code_diff,
        suggested_code=ai_resp.suggested_code,
        tokens_consumed=ai_resp.tokens_consumed
    )
    db.add(assistant_msg)
    await db.commit()
    await db.refresh(assistant_msg)

    return AIMessageResponse.model_validate(assistant_msg)

@router.get("/conversations", response_model=List[AIConversationResponse])
async def list_conversations(
    project_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(AIConversation).where(AIConversation.user_id == current_user.id)
    if project_id:
        stmt = stmt.where(AIConversation.project_id == project_id)
    stmt = stmt.order_by(desc(AIConversation.updated_at))
    res = await db.execute(stmt)
    convs = list(res.scalars().all())
    return [AIConversationResponse.model_validate(c) for c in convs]

@router.get("/conversations/{conv_id}", response_model=AIConversationResponse)
async def get_conversation(
    conv_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(AIConversation).where(AIConversation.id == conv_id)
    conv = (await db.execute(stmt)).scalar_one_or_none()
    if not conv or conv.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Conversation not found or unauthorized.")
    return AIConversationResponse.model_validate(conv)

@router.delete("/conversations/{conv_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conv_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(AIConversation).where(AIConversation.id == conv_id)
    conv = (await db.execute(stmt)).scalar_one_or_none()
    if not conv or conv.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Conversation not found or unauthorized.")
    await db.delete(conv)
    await db.commit()
    return None
