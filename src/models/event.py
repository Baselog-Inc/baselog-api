from sqlalchemy import Column, String, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from src.models.base import Base


def validate_event_format(event_type: str) -> bool:
    """Validate event type format without restrictive constraints"""
    return (
        len(event_type) <= 255 and
        event_type.strip() and
        # Basic format validation - alphanumeric, underscore, hyphen, space
        all(c.isalnum() or c in ['_', '-', ' ', '.'] for c in event_type.strip())
    )


class Event(Base):
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    event_type = Column(String(255), nullable=False)
    event_status = Column(String(50), nullable=True)
    event_metadata = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship with Project
    project = relationship("Project", back_populates="events")