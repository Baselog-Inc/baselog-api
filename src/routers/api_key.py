from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from src.core.auth import get_current_user
from src.models.user import User
from src.core.project import get_user_project
from src.models.base import get_db
from sqlalchemy.orm import Session
from src.models.project import Project

router = APIRouter(prefix="/api-keys", tags=["api-keys"])


class APIKeyCreate(BaseModel):
    description: Optional[str] = None


class APIKeyResponse(BaseModel):
    api_key: str
    masked_key: str
    created_at: datetime
    description: Optional[str] = None


class ProjectWithAPIKeyResponse(BaseModel):
    id: str
    name: str
    owner_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    api_key: Optional[str] = None
    api_key_masked: Optional[str] = None
    api_key_created_at: Optional[datetime] = None


@router.post("/projects/{project_id}/api-keys", response_model=APIKeyResponse, status_code=status.HTTP_201_CREATED)
async def generate_project_api_key(
    project_id: str,
    api_key_data: APIKeyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # V�rifier que l'utilisateur est propri�taire du projet
    project_result = get_user_project(project_id, str(current_user.id), db)
    if project_result.is_err():
        raise project_result.unwrap_err()

    # Dummy data
    dummy_api_key = "sk_proj_dummy_key_1234567890abcdefghijklmnopqrstuvwxyz"
    masked_key = "sk_proj_dum******************"
    created_at = datetime.utcnow()

    return APIKeyResponse(
        api_key=dummy_api_key,
        masked_key=masked_key,
        created_at=created_at,
        description=api_key_data.description
    )


@router.get("/projects/{project_id}/api-keys", response_model=APIKeyResponse)
async def get_project_api_key(
    project_id: str,
    show_full: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # V�rifier que l'utilisateur est propri�taire du projet
    project_result = get_user_project(project_id, str(current_user.id), db)
    if project_result.is_err():
        raise project_result.unwrap_err()

    # Dummy data
    dummy_api_key = "sk_proj_dummy_key_1234567890abcdefghijklmnopqrstuvwxyz"
    masked_key = "sk_proj_dum******************"
    created_at = datetime.utcnow()

    api_key_to_show = dummy_api_key if show_full else None

    return APIKeyResponse(
        api_key=api_key_to_show,
        masked_key=masked_key,
        created_at=created_at,
        description=None
    )


@router.delete("/projects/{project_id}/api-keys", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_api_key(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # V�rifier que l'utilisateur est propri�taire du projet
    project_result = get_user_project(project_id, str(current_user.id), db)
    if project_result.is_err():
        raise project_result.unwrap_err()

    # Just return 204 No Content for dummy implementation
    return


@router.get("/projects/{project_id}", response_model=ProjectWithAPIKeyResponse)
async def get_project_with_api_key(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # V�rifier que l'utilisateur est propri�taire du projet
    project_result = get_user_project(project_id, str(current_user.id), db)
    if project_result.is_err():
        raise project_result.unwrap_err()

    project = project_result.unwrap()

    # Dummy data
    masked_key = "sk_proj_dum******************"

    return ProjectWithAPIKeyResponse(
        id=str(project.id),
        name=project.name,
        owner_id=str(project.owner_id),
        created_at=project.created_at,
        updated_at=project.updated_at,
        api_key=None,
        api_key_masked=masked_key,
        api_key_created_at=datetime.utcnow()
    )