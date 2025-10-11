from collections.abc import Sequence
from typing import List, Optional
from sqlalchemy.orm import Session
from src.models.event import Event, validate_event_format
from src.models.project import Project
from src.core.project import check_project_ownership
from src.utils.result import Result, Ok, Err
from fastapi import HTTPException, status


def create_event(
    project_id: str, event_data: dict, db: Session
) -> Result[Event, HTTPException]:
    try:
        # Validate event format
        if "event_type" in event_data and not validate_event_format(event_data["event_type"]):
            return Err(
                HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid event type format. Must be 255 characters or less and contain only alphanumeric, underscore, hyphen, space, and dot characters",
                )
            )

        # Create the event
        new_event = Event(
            project_id=project_id,
            event_type=event_data["event_type"],
            event_status=event_data.get("event_status"),
            event_metadata=event_data.get("event_metadata", {}),
        )

        db.add(new_event)
        db.commit()
        db.refresh(new_event)

        return Ok(new_event)

    except Exception as e:
        return Err(
            HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create event: {e}",
            )
        )


def get_events_by_project(
    project_id: str, user_id: str, db: Session
) -> Result[List[Event], HTTPException]:
    try:
        # Check project ownership
        project_result = check_project_ownership(project_id, user_id, db)
        if project_result.is_err():
            return Err(project_result.unwrap_err())

        events = (
            db.query(Event)
            .filter(Event.project_id == project_id)
            .order_by(Event.created_at.desc())
            .all()
        )

        return Ok(events)

    except Exception as e:
        return Err(
            HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred",
            )
        )


def get_event_by_id(
    event_id: str, user_id: str, db: Session
) -> Result[Event, HTTPException]:
    try:
        # Get event and check project access
        event = (
            db.query(Event)
            .join(Project)
            .filter(Event.id == event_id, Project.owner_id == user_id)
            .first()
        )

        if event is None:
            return Err(
                HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Event not found or access denied",
                )
            )

        return Ok(event)

    except Exception as e:
        return Err(
            HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred",
            )
        )


def update_event(
    event_id: str, event_data: dict, user_id: str, db: Session
) -> Result[Event, HTTPException]:
    try:
        # Check if event exists and user has access
        event_result = get_event_by_id(event_id, user_id, db)
        if event_result.is_err():
            return Err(event_result.unwrap_err())

        event = event_result.unwrap()

        # Validate event format if provided
        if "event_type" in event_data and not validate_event_format(event_data["event_type"]):
            return Err(
                HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid event type format",
                )
            )

        # Validate status transition if status is being updated
        if "event_status" in event_data:
            status_transition_result = validate_status_transition(
                event.event_status, event_data["event_status"]
            )
            if not status_transition_result:
                return Err(
                    HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid status transition",
                    )
                )

        # Update fields
        if "event_type" in event_data:
            event.event_type = event_data["event_type"]
        if "event_status" in event_data:
            event.event_status = event_data["event_status"]
        if "event_metadata" in event_data:
            event.event_metadata = event_data["event_metadata"]

        db.commit()
        db.refresh(event)

        return Ok(event)

    except Exception as e:
        return Err(
            HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update event",
            )
        )


def delete_event(
    event_id: str, user_id: str, db: Session
) -> Result[bool, HTTPException]:
    try:
        # Check if event exists and user has access
        event_result = get_event_by_id(event_id, user_id, db)
        if event_result.is_err():
            return Err(event_result.unwrap_err())

        event = event_result.unwrap()

        # Delete the event
        db.delete(event)
        db.commit()

        return Ok(True)

    except Exception as e:
        return Err(
            HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete event",
            )
        )


def validate_event_format(event_type: str) -> bool:
    """Validate event type format"""
    return (
        len(event_type) <= 255 and
        event_type.strip() and
        # Basic format validation - alphanumeric, underscore, hyphen, space, dot
        all(c.isalnum() or c in ['_', '-', ' ', '.'] for c in event_type.strip())
    )


def validate_status_transition(
    old_status: Optional[str], new_status: str
) -> bool:
    """Validate status transition for events with status"""
    # If event has no status, allow setting any status
    if old_status is None:
        return True

    # If status is being cleared, allow it
    if new_status is None:
        return True

    # Basic validation - allow any transition for MVP
    # More complex business logic can be added later
    return (
        len(new_status) <= 50 and
        new_status.strip() and
        all(c.isalnum() or c in ['_', '-', ' ', '.'] for c in new_status.strip())
    )