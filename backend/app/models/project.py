import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.models.base import TimeStampedModel, GUID

class Project(TimeStampedModel):
    __tablename__ = "projects"

    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    experiment_id = Column(GUID(), ForeignKey("experiments.id", ondelete="SET NULL"), nullable=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    default_engine = Column(String(20), nullable=False, default="octave") # 'octave' | 'python'
    is_public = Column(Boolean, default=False, nullable=False)

    user = relationship("User", back_populates="projects")
    experiment = relationship("Experiment", back_populates="projects")
    files = relationship("ProjectFile", back_populates="project", cascade="all, delete-orphan", lazy="selectin")
    executions = relationship("Execution", back_populates="project", cascade="all, delete-orphan")
    reports = relationship("GeneratedReport", back_populates="project", cascade="all, delete-orphan")

class ProjectFile(TimeStampedModel):
    __tablename__ = "project_files"

    project_id = Column(GUID(), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    path = Column(String(500), nullable=False)
    content = Column(Text, nullable=False, default="")
    is_entrypoint = Column(Boolean, nullable=False, default=False)

    project = relationship("Project", back_populates="files")
