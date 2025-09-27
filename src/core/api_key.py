from sqlalchemy.orm import Session
from src.models.api_key import APIKey
from src.utils.api_key import generate_api_key, hash_api_key, create_masked_key, verify_api_key, is_api_key_valid
from src.models.base import get_db
from datetime import datetime
from typing import Optional, List

def create_api_key(
    project_id: str,
    db: Session,
    description: Optional[str] = None
) -> Optional[APIKey]:
    try:
        full_key, key_hash, masked_key = generate_api_key()
        api_key = APIKey(
            project_id=project_id,
            key_hash=key_hash,
            masked_key=masked_key,
            description=description,
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.add(api_key)
        db.commit()
        db.refresh(api_key)
        return api_key
    except Exception as e:
        db.rollback()
        return None

def get_project_api_key(project_id: str, db: Session) -> Optional[APIKey]:
    return db.query(APIKey).filter(
        APIKey.project_id == project_id,
        APIKey.is_active == True
    ).first()

def get_api_key_by_key_hash(key_hash: str, db: Session) -> Optional[APIKey]:
    return db.query(APIKey).filter(
        APIKey.key_hash == key_hash,
        APIKey.is_active == True
    ).first()

def update_api_key_usage(api_key_id: str, db: Session) -> bool:
    try:
        api_key = db.query(APIKey).filter(APIKey.id == api_key_id).first()
        if api_key:
            api_key.last_used_at = datetime.utcnow()
            db.commit()
            return True
        return False
    except Exception:
        db.rollback()
        return False

def deactivate_api_key(project_id: str, db: Session) -> bool:
    try:
        api_key = db.query(APIKey).filter(
            APIKey.project_id == project_id,
            APIKey.is_active == True
        ).first()
        if api_key:
            api_key.is_active = False
            db.commit()
            return True
        return False
    except Exception:
        db.rollback()
        return False

def regenerate_api_key(
    project_id: str,
    db: Session,
    description: Optional[str] = None
) -> Optional[APIKey]:
    try:
        deactivate_api_key(project_id, db)
        return create_api_key(project_id, db, description)
    except Exception:
        db.rollback()
        return None

def get_all_active_api_keys(db: Session) -> List[APIKey]:
    return db.query(APIKey).filter(APIKey.is_active == True).all()