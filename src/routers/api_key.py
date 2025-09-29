from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from src.core.auth import get_current_user
from src.core.project import check_project_ownership
from src.core.api_key import get_api_key_by_project, create_api_key, reset_api_key
from src.models.user import User
from src.models.base import get_db
from sqlalchemy.orm import Session
from uuid import uuid4

router = APIRouter(prefix="/api-keys", tags=["api-keys"])


class APIKeyResponse(BaseModel):
    id: str
    key: str
    project_id: str
    active: bool
    created_at: datetime
    last_used: Optional[datetime] = None

    @classmethod
    def from_dummy(cls, project_id: str):
        return cls(
            id=str(uuid4()),
            key="sk_live_" + "".join([str(i) for i in range(32)]),
            project_id=project_id,
            active=True,
            created_at=datetime.now(),
            last_used=None
        )


class APIKeyResetResponse(BaseModel):
    new_key: str
    message: str




@router.get("/projects/{project_id}", response_model=APIKeyResponse)
async def get_api_key(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Vérifier que l'utilisateur est propriétaire du projet
    ownership_check = check_project_ownership(project_id, str(current_user.id), db)
    if ownership_check.is_err():
        raise ownership_check.unwrap_err()

    api_key_obj = get_api_key_by_project(project_id, db)
    if not api_key_obj:
        raise HTTPException(status_code=404, detail="API Key not found")

    return APIKeyResponse(
        id=str(api_key_obj.id),
        project_id=str(api_key_obj.project_id),
        active=api_key_obj.is_active,
        created_at=api_key_obj.created_at,
        last_used=api_key_obj.last_used_at
    )


@router.post("/projects/{project_id}/generate", response_model=APIKeyResponse, status_code=status.HTTP_201_CREATED)
async def generate_api_key_route(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Vérifier que l'utilisateur est propriétaire du projet
    ownership_check = check_project_ownership(project_id, str(current_user.id), db)
    if ownership_check.is_err():
        raise ownership_check.unwrap_err()

    api_key_obj, key = create_api_key(project_id, db)
    return APIKeyResponse(
        id=str(api_key_obj.id),
        key=key,
        project_id=str(api_key_obj.project_id),
        active=api_key_obj.is_active,
        created_at=api_key_obj.created_at,
        last_used=api_key_obj.last_used_at
    )


@router.post("/projects/{project_id}/reset", response_model=APIKeyResetResponse)
async def reset_api_key_route(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Vérifier que l'utilisateur est propriétaire du projet
    ownership_check = check_project_ownership(project_id, str(current_user.id), db)
    if ownership_check.is_err():
        raise ownership_check.unwrap_err()

    api_key_obj = reset_api_key(project_id, db)
    return APIKeyResetResponse(
        new_key="***",  # We don't return the actual key for security
        message="API key has been reset successfully"
    )


@router.get("/projects/{project_id}/status")
async def get_api_key_status(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Vérifier que l'utilisateur est propriétaire du projet
    ownership_check = check_project_ownership(project_id, str(current_user.id), db)
    if ownership_check.is_err():
        raise ownership_check.unwrap_err()

    api_key_obj = get_api_key_by_project(project_id, db)
    if not api_key_obj:
        raise HTTPException(status_code=404, detail="API Key not found")

    return {
        "project_id": project_id,
        "active": api_key_obj.is_active,
        "created_at": api_key_obj.created_at,
        "last_used": api_key_obj.last_used_at,
        "can_reset": True
    }