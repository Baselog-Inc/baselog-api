from typing import Optional
from datetime import datetime
from src.models.base import get_db
from src.models.api_key import APIKey
from src.models.project import Project
from src.utils.api_key import generate_api_key, hash_key, verify_key_hash
from sqlalchemy.orm import Session

def create_api_key(project_id: str, db: Session) -> tuple[APIKey, str]:
    """Create and save a new API key for a project. Returns (api_key, key_string)."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise ValueError("Project not found")

    existing_key = db.query(APIKey).filter(APIKey.project_id == project_id).first()
    if existing_key:
        existing_key.is_active = False
        db.commit()

    key = generate_api_key()
    key_hash = hash_key(key)

    api_key = APIKey(
        key_hash=key_hash,
        project_id=project_id,
        is_active=True,
        created_at=datetime.now()
    )

    db.add(api_key)
    db.commit()
    db.refresh(api_key)

    return api_key, key

def get_api_key_by_key(key: str, db: Session) -> Optional[APIKey]:
    """Get API key by key string for authentication."""
    # First get all potential matches by key_hash
    key_hash = hash_key(key)
    api_key = db.query(APIKey).filter(APIKey.key_hash == key_hash, APIKey.is_active == True).first()

    if api_key and verify_key_hash(key, api_key.key_hash):
        return api_key

    return None

def get_api_key_by_project(project_id: str, db: Session) -> Optional[APIKey]:
    """Get active API key by project ID."""
    return db.query(APIKey).filter(APIKey.project_id == project_id, APIKey.is_active == True).first()

def reset_api_key(project_id: str, db: Session) -> APIKey:
    """Reset API key for a project (deactivate old, create new)."""
    return create_api_key(project_id, db)

def deactivate_api_key(project_id: str, db: Session) -> bool:
    """Deactivate API key for a project."""
    api_key = db.query(APIKey).filter(APIKey.project_id == project_id, APIKey.is_active == True).first()
    if not api_key:
        return False

    api_key.is_active = False
    api_key.updated_at = datetime.now()
    db.commit()
    return True

def get_active_api_keys(project_id: str, db: Session) -> list[APIKey]:
    """Get all active API keys for a project."""
    return db.query(APIKey).filter(APIKey.project_id == project_id, APIKey.is_active == True).all()