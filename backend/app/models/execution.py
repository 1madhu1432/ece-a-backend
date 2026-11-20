import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, ForeignKey, Integer, BigInteger, Text, JSON, DateTime
from sqlalchemy.orm import relationship
from app.models.base import TimeStampedModel, GUID

class Execution(TimeStampedModel):
    __tablename__ = "executions"

    project_id = Column(GUID(), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    file_id = Column(GUID(), ForeignKey("project_files.id", ondelete="SET NULL"), nullable=True)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    engine = Column(String(20), nullable=False, default="octave") # 'octave' | 'python'
    status = Column(String(20), nullable=False, default="queued") # queued, running, completed, failed, timeout, cancelled
    exit_code = Column(Integer, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    cpu_time_ms = Column(Integer, nullable=True)
    peak_memory_bytes = Column(BigInteger, nullable=True)
    submitted_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="executions")
    project = relationship("Project", back_populates="executions")
    results = relationship("ExecutionResult", back_populates="execution", uselist=False, cascade="all, delete-orphan", lazy="selectin")
    artifacts = relationship("ExecutionArtifact", back_populates="execution", cascade="all, delete-orphan", lazy="selectin")

class ExecutionResult(TimeStampedModel):
    __tablename__ = "execution_results"

    execution_id = Column(GUID(), ForeignKey("executions.id", ondelete="CASCADE"), unique=True, nullable=False)
    stdout = Column(Text, nullable=False, default="")
    stderr = Column(Text, nullable=False, default="")
    variables_json = Column(JSON, nullable=False, default=dict)
    error_summary = Column(Text, nullable=True)

    execution = relationship("Execution", back_populates="results")

class ExecutionArtifact(TimeStampedModel):
    __tablename__ = "execution_artifacts"

    execution_id = Column(GUID(), ForeignKey("executions.id", ondelete="CASCADE"), nullable=False, index=True)
    artifact_type = Column(String(50), nullable=False) # figure_png, figure_svg, plotly_json, report_pdf
    storage_key = Column(String(500), nullable=False)
    filename = Column(String(255), nullable=False)
    file_size_bytes = Column(BigInteger, nullable=False, default=0)
    mime_type = Column(String(100), nullable=False)

    execution = relationship("Execution", back_populates="artifacts")
