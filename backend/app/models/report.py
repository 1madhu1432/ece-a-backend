import uuid
from sqlalchemy import Column, String, ForeignKey, Text, JSON, Integer, Boolean
from sqlalchemy.orm import relationship
from app.models.base import TimeStampedModel, GUID

class GeneratedReport(TimeStampedModel):
    __tablename__ = "generated_reports"

    project_id = Column(GUID(), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    execution_id = Column(GUID(), ForeignKey("executions.id", ondelete="SET NULL"), nullable=True)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    pdf_storage_key = Column(String(500), nullable=False)
    sections_json = Column(JSON, nullable=False, default=dict)

    user = relationship("User", back_populates="reports")
    project = relationship("Project", back_populates="reports")

class Subscription(TimeStampedModel):
    __tablename__ = "subscriptions"

    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    tier = Column(String(20), nullable=False, default="free") # free, basic, pro, premium
    monthly_execution_quota = Column(Integer, nullable=False, default=100)
    monthly_ai_token_quota = Column(Integer, nullable=False, default=50000)
    quota_reset_at = Column(TimeStampedModel.created_at.type, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)

    user = relationship("User", back_populates="subscription")

class AuditLog(TimeStampedModel):
    __tablename__ = "audit_logs"

    user_id = Column(GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(100), nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    details_json = Column(JSON, nullable=False, default=dict)

    user = relationship("User", back_populates="audit_logs")
