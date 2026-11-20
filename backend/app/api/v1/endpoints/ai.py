from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
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
    # 1. Find or create conversation
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

    # 2. Record User Message
    user_msg = AIMessage(
        conversation_id=conv_id,
        sender="user",
        agent_role=req.agent_role,
        content=req.prompt,
        tokens_consumed=0
    )
    db.add(user_msg)
    await db.flush()

    # 3. Retrieve recent history
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

    # 4. Invoke Multi-Agent Orchestrator
    ai_resp = await orchestrator.process_chat(
        prompt=req.prompt,
        agent_role=req.agent_role,
        conversation_history=chat_history,
        active_code=req.active_code,
        selected_code=req.selected_code,
        last_error=req.last_error
    )

    # 5. Record Assistant Message
    assistant_msg = AIMessage(
        conversation_id=conv_id,
        sender="assistant",
        agent_role=req.agent_role,
        content=ai_resp.content,
        code_diff=ai_resp.code_diff,
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
