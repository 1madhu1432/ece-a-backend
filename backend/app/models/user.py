import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, ForeignKey, Integer, Enum as SQLEnum, JSON, DateTime, Text
from sqlalchemy.orm import relationship
from app.models.base import TimeStampedModel, GUID

class User(TimeStampedModel):
    __tablename__ = "users"

    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="student") # student, admin
    is_verified = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    verification_token = Column(String(255), nullable=True)
    password_reset_token = Column(String(255), nullable=True)

    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan", lazy="selectin")
    subscription = relationship("Subscription", back_populates="user", uselist=False, cascade="all, delete-orphan", lazy="selectin")
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    executions = relationship("Execution", back_populates="user", cascade="all, delete-orphan")
    ai_conversations = relationship("AIConversation", back_populates="user", cascade="all, delete-orphan")
    reports = relationship("GeneratedReport", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")

class UserProfile(TimeStampedModel):
    __tablename__ = "user_profiles"

    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    full_name = Column(String(150), nullable=False)
    college_name = Column(String(255), nullable=True)
    branch = Column(String(100), default="ECE")
    academic_year = Column(Integer, default=3)
    avatar_url = Column(Text, nullable=True)

    user = relationship("User", back_populates="profile")
