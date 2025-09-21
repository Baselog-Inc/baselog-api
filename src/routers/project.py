from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from src.core.auth import get_current_user
from src.models.user import User
from src.core.project import (
    create_project,
    get_projects_by_user,
    get_user_project,
    update_project,
    delete_project,
)
from src.models.base import get_db
from sqlalchemy.orm import Session
from src.models.project import Project

router = APIRouter(prefix="/projects", tags=["projects"])


class ProjectCreate(BaseModel):
    name: str


class ProjectResponse(BaseModel):
    id: str
    name: str
    owner_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    @classmethod
    def from_orm(cls, project):
        return cls(
            id=str(project.id),
            name=project.name,
            owner_id=str(project.owner_id),
            created_at=project.created_at,
            updated_at=project.updated_at
        )


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project_route(
    project: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = create_project({"name": project.name}, db, current_user)
    if result.is_err():
        raise result.unwrap()
    return ProjectResponse.from_orm(result.unwrap())


@router.get("/", response_model=List[ProjectResponse])
async def get_user_projects(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    result = get_projects_by_user(str(current_user.id), db)
    if result.is_err():
        raise result.unwrap()
    return [ProjectResponse.from_orm(project) for project in result.unwrap()]


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = get_user_project(project_id, str(current_user.id), db)
    if result.is_err():
        raise result.unwrap()
    return ProjectResponse.from_orm(result.unwrap())


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project_route(
    project_id: str,
    project_update: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = update_project(
        project_id, {"name": project_update.name}, str(current_user.id), db
    )
    if result.is_err():
        raise result.unwrap_err()
    return ProjectResponse.from_orm(result.unwrap())


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_route(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = delete_project(project_id, str(current_user.id), db)
    if result.is_err():
        raise result.unwrap()
    return
