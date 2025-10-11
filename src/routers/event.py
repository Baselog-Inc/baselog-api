from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from src.core.auth import get_current_user
from src.core.project import check_project_ownership
from src.core.api_key import get_api_key_by_key
from src.models.user import User
from src.models.event import Event
from src.models.api_key import APIKey
from src.core.event import (
    create_event,
    get_events_by_project,
    get_event_by_id,
    update_event,
    delete_event,
)
from src.models.base import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/projects", tags=["events"])
api_key_scheme = APIKeyHeader(name="X-API-Key")


class EventCreate(BaseModel):
    event_type: str
    event_status: Optional[str] = None
    metadata: Optional[dict] = {}


class EventResponse(BaseModel):
    id: str
    project_id: str
    event_type: str
    event_status: Optional[str]
    metadata: dict
    created_at: datetime
    updated_at: Optional[datetime]

    @classmethod
    def from_orm(cls, event: Event):
        return cls(
            id=str(event.id),
            project_id=str(event.project_id),
            event_type=event.event_type,
            event_status=event.event_status,
            metadata=event.event_metadata,
            created_at=event.created_at,
            updated_at=event.updated_at
        )


class EventUpdate(BaseModel):
    event_status: Optional[str] = None
    metadata: Optional[dict] = None


async def get_api_key_dep(api_key: str = Depends(api_key_scheme), db: Session = Depends(get_db)) -> APIKey:
    """Authenticate API key and return API key object."""
    api_key_obj = get_api_key_by_key(api_key, db)
    if not api_key_obj:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    if not api_key_obj.is_active:
        raise HTTPException(status_code=403, detail="API Key is not active")
    return api_key_obj


# User endpoints (Bearer token authentication)
@router.get("/{project_id}/events")
async def get_events_route(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of events to return"),
    offset: int = Query(0, ge=0, description="Number of events to skip"),
):
    """Get all events for a project with pagination support."""
    result = get_events_by_project(project_id, str(current_user.id), db)
    if result.is_err():
        raise result.unwrap_err()

    events = result.unwrap()
    # Apply pagination
    paginated_events = events[offset:offset + limit]
    return [EventResponse.from_orm(event) for event in paginated_events]


@router.get("/{project_id}/events/{event_id}")
async def get_event_route(
    project_id: str,
    event_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific event by ID."""
    result = get_event_by_id(event_id, str(current_user.id), db)
    if result.is_err():
        raise result.unwrap_err()
    return EventResponse.from_orm(result.unwrap())


@router.post("/{project_id}/events", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event_route(
    project_id: str,
    event_data: EventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new event."""
    result = create_event(project_id, event_data.dict(), db)
    if result.is_err():
        raise result.unwrap_err()
    return EventResponse.from_orm(result.unwrap())


@router.put("/{project_id}/events/{event_id}", response_model=EventResponse)
async def update_event_route(
    project_id: str,
    event_id: str,
    event_data: EventUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update an existing event."""
    result = update_event(event_id, event_data.dict(exclude_unset=True), str(current_user.id), db)
    if result.is_err():
        raise result.unwrap_err()
    return EventResponse.from_orm(result.unwrap())


@router.delete("/{project_id}/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event_route(
    project_id: str,
    event_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete an event."""
    result = delete_event(event_id, str(current_user.id), db)
    if result.is_err():
        raise result.unwrap_err()
    return


# SDK endpoints (API Key authentication)
@router.post("/events", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event_api_key_route(
    event_data: EventCreate,
    api_key: APIKey = Depends(get_api_key_dep),
    db: Session = Depends(get_db),
) -> EventResponse:
    """Create event using API key project ID (SDK endpoint)."""
    # Extract project_id from validated API key
    project_id = str(api_key.project_id)

    if not project_id:
        raise HTTPException(status_code=400, detail="API key not associated with a project")

    # Use existing core logic to create event
    result = create_event(project_id, event_data.dict(), db)
    if result.is_err():
        raise result.unwrap()

    return EventResponse.from_orm(result.unwrap())