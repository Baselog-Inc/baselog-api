from sqlalchemy import Column, String, DateTime, func, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import hashlib
from .base import Base

class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), unique=True, nullable=False)
    key_hash = Column(String(64), nullable=False)  # SHA-256 hash
    masked_key = Column(String(32), nullable=False)  # sk_proj_******************
    description = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used_at = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)

    # Relationships
    project = relationship("Project", back_populates="api_key")