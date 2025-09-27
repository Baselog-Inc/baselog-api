from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from src.core.auth import get_current_user
from src.models.user import User
from src.models.log import Log
from src.core.log import (
    create_log,
    get_logs_by_project,
    get_log_by_id,
    update_log,
    delete_log,
    get_logs_by_level,
    get_logs_by_category,
    get_logs_by_tag
)
from src.models.base import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/projects", tags=["logs"])


class LogCreate(BaseModel):
    level: str = "info"
    category: Optional[str] = None
    message: str
    tags: Optional[List[str]] = []


class LogResponse(BaseModel):
    id: str
    project_id: str
    level: str
    category: Optional[str]
    message: str
    tags: Optional[List[str]]
    created_at: datetime
    updated_at: Optional[datetime]

    @classmethod
    def from_orm(cls, log: Log):
        return cls(
            id=str(log.id),
            project_id=str(log.project_id),
            level=log.level,
            category=log.category,
            message=log.message,
            tags=log.tags,
            created_at=log.created_at,
            updated_at=log.updated_at
        )


class LogUpdate(BaseModel):
    level: Optional[str] = None
    category: Optional[str] = None
    message: Optional[str] = None
    tags: Optional[List[str]] = None


@router.post("/{project_id}/logs", response_model=LogResponse, status_code=status.HTTP_201_CREATED)
async def create_log_route(
    project_id: str,
    log_data: LogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = create_log(project_id, log_data.dict(), db, current_user)
    if result.is_err():
        raise result.unwrap()
    return LogResponse.from_orm(result.unwrap())


@router.get("/{project_id}/logs", response_model=List[LogResponse])
async def get_user_logs_route(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = get_logs_by_project(project_id, str(current_user.id), db)
    if result.is_err():
        raise result.unwrap()
    return [LogResponse.from_orm(log) for log in result.unwrap()]


@router.get("/{project_id}/logs/{log_id}", response_model=LogResponse)
async def get_log_route(
    project_id: str,
    log_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = get_log_by_id(log_id, str(current_user.id), db)
    if result.is_err():
        raise result.unwrap()
    return LogResponse.from_orm(result.unwrap())


@router.put("/{project_id}/logs/{log_id}", response_model=LogResponse)
async def update_log_route(
    project_id: str,
    log_id: str,
    log_data: LogUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = update_log(log_id, log_data.dict(exclude_unset=True), str(current_user.id), db)
    if result.is_err():
        raise result.unwrap_err()
    return LogResponse.from_orm(result.unwrap())


@router.delete("/{project_id}/logs/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_log_route(
    project_id: str,
    log_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = delete_log(log_id, str(current_user.id), db)
    if result.is_err():
        raise result.unwrap()
    return


@router.get("/{project_id}/logs/level/{level}", response_model=List[LogResponse])
async def get_logs_by_level_route(
    project_id: str,
    level: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = get_logs_by_level(project_id, level, str(current_user.id), db)
    if result.is_err():
        raise result.unwrap()
    return [LogResponse.from_orm(log) for log in result.unwrap()]


@router.get("/{project_id}/logs/category/{category}", response_model=List[LogResponse])
async def get_logs_by_category_route(
    project_id: str,
    category: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = get_logs_by_category(project_id, category, str(current_user.id), db)
    if result.is_err():
        raise result.unwrap()
    return [LogResponse.from_orm(log) for log in result.unwrap()]


@router.get("/{project_id}/logs/tag/{tag}", response_model=List[LogResponse])
async def get_logs_by_tag_route(
    project_id: str,
    tag: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = get_logs_by_tag(project_id, tag, str(current_user.id), db)
    if result.is_err():
        raise result.unwrap()
    return [LogResponse.from_orm(log) for log in result.unwrap()]