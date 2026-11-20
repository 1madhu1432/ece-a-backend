import uuid
from sqlalchemy import Column, String, ForeignKey, Integer, Text, JSON
from sqlalchemy.orm import relationship
from app.models.base import TimeStampedModel, GUID

class ExperimentCategory(TimeStampedModel):
    __tablename__ = "experiment_categories"

    name = Column(String(100), unique=True, nullable=False)
    code = Column(String(50), unique=True, nullable=False) # DSP, COMM, CONTROL
    description = Column(Text, nullable=True)
    display_order = Column(Integer, default=0)

    experiments = relationship("Experiment", back_populates="category", cascade="all, delete-orphan")

class Experiment(TimeStampedModel):
    __tablename__ = "experiments"

    category_id = Column(GUID(), ForeignKey("experiment_categories.id", ondelete="RESTRICT"), nullable=False)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    objective = Column(Text, nullable=False)
    theory = Column(Text, nullable=False)
    equations_json = Column(JSON, nullable=False, default=list)
    procedure_json = Column(JSON, nullable=False, default=list)
    default_code = Column(Text, nullable=False)
    engine = Column(String(20), nullable=False, default="octave")
    expected_output = Column(Text, nullable=True)
    matlab_code = Column(Text, nullable=True)
    python_code = Column(Text, nullable=True)
    viva_questions_json = Column(JSON, nullable=True, default=list)

    category = relationship("ExperimentCategory", back_populates="experiments")
    projects = relationship("Project", back_populates="experiment")
