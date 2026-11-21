import uuid
from sqlalchemy import Column, String, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship
from app.models.base import TimeStampedModel, GUID

class AIConversation(TimeStampedModel):
    __tablename__ = "ai_conversations"

    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(GUID(), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True)
    title = Column(String(200), nullable=False, default="New Conversation")

    user = relationship("User", back_populates="ai_conversations")
    messages = relationship("AIMessage", back_populates="conversation", cascade="all, delete-orphan", lazy="selectin")

class AIMessage(TimeStampedModel):
    __tablename__ = "ai_messages"

    conversation_id = Column(GUID(), ForeignKey("ai_conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    sender = Column(String(20), nullable=False) # 'user', 'assistant', 'system'
    agent_role = Column(String(50), nullable=False, default="ECE Tutor")
    content = Column(Text, nullable=False)
    code_diff = Column(Text, nullable=True)
    suggested_code = Column(Text, nullable=True)
    tokens_consumed = Column(Integer, nullable=False, default=0)

    conversation = relationship("AIConversation", back_populates="messages")
