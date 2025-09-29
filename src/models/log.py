from sqlalchemy import Column, String, DateTime, func, ForeignKey, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import relationship
import uuid
from enum import Enum as PyEnum
from src.models.base import Base

class LogLevel(PyEnum):
    INFO = "info"
    DEBUG = "debug"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class Log(Base):
    __tablename__ = "logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    level = Column(String(50), nullable=False)
    category = Column(String(255), nullable=True)
    message = Column(Text, nullable=False)
    tags = Column(ARRAY(String), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship with Project
    project = relationship("Project", back_populates="logs")