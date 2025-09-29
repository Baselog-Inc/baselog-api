from collections.abc import Sequence
from sqlalchemy.orm import Session
from typing import List, Optional
from src.models.base import get_db
from src.models.project import Project
from src.models.log import Log, LogLevel
from src.models.user import User
from src.core.project import check_project_ownership
from src.utils.result import Result, Ok, Err
from fastapi import HTTPException, status


def validate_log_level(level: str) -> bool:
    """Valide si le niveau de log est valide"""
    return level.lower() in [member.value for member in LogLevel]


def create_log(
    project_id: str, log_data: dict, db: Session
) -> Result[Log, HTTPException]:
    try:
        # Vérifier si le projet existe et appartient à l'utilisateur
        # Valider le niveau de log
        if "level" in log_data and not validate_log_level(log_data["level"]):
            return Err(
                HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid log level. Must be: info, debug, warning, error, critical",
                )
            )

        # Créer le log
        new_log = Log(
            project_id=project_id,
            level=log_data.get("level", "info").upper(),
            category=log_data.get("category"),
            message=log_data["message"],
            tags=log_data.get("tags"),
        )

        db.add(new_log)
        db.commit()
        db.refresh(new_log)

        return Ok(new_log)

    except Exception as e:
        return Err(
            HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create log: {e}",
            )
        )


def get_logs_by_project(
    project_id: str, user_id: str, db: Session
) -> Result[List[Log], HTTPException]:
    try:
        # Vérifier si l'utilisateur a accès au projet
        project_result = check_project_ownership(project_id, user_id, db)
        if project_result.is_err():
            return Err(project_result.unwrap_err())

        logs = (
            db.query(Log)
            .filter(Log.project_id == project_id)
            .order_by(Log.created_at.desc())
            .all()
        )

        return Ok(logs)

    except Exception as e:
        return Err(
            HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred",
            )
        )


def get_log_by_id(log_id: str, user_id: str, db: Session) -> Result[Log, HTTPException]:
    try:
        # Récupérer le log et vérifier l'accès au projet
        log = (
            db.query(Log)
            .join(Project)
            .filter(Log.id == log_id, Project.owner_id == user_id)
            .first()
        )

        if log is None:
            return Err(
                HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Log not found or access denied",
                )
            )

        return Ok(log)

    except Exception as e:
        return Err(
            HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred",
            )
        )


def update_log(
    log_id: str, log_data: dict, user_id: str, db: Session
) -> Result[Log, HTTPException]:
    try:
        # Vérifier si le log existe et l'utilisateur a les droits
        log_result = get_log_by_id(log_id, user_id, db)
        if log_result.is_err():
            return Err(log_result.unwrap_err())

        log = log_result.unwrap()

        # Valider les données si fournies
        if "level" in log_data and not validate_log_level(log_data["level"]):
            return Err(
                HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid log level. Must be: info, debug, warning, error, critical",
                )
            )

        # Mettre à jour les champs
        if "level" in log_data:
            log.level = log_data["level"].lower()
        if "category" in log_data:
            log.category = log_data["category"]
        if "message" in log_data:
            log.message = log_data["message"]
        if "tags" in log_data:
            log.tags = log_data["tags"]

        db.commit()
        db.refresh(log)

        return Ok(log)

    except Exception as e:
        return Err(
            HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update log",
            )
        )


def delete_log(log_id: str, user_id: str, db: Session) -> Result[bool, HTTPException]:
    try:
        # Vérifier si le log existe et l'utilisateur a les droits
        log_result = get_log_by_id(log_id, user_id, db)
        if log_result.is_err():
            return Err(log_result.unwrap_err())

        log = log_result.unwrap()

        # Supprimer le log
        db.delete(log)
        db.commit()

        return Ok(True)

    except Exception as e:
        return Err(
            HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete log",
            )
        )


def get_logs_by_level(
    project_id: str, level: str, user_id: str, db: Session
) -> Result[List[Log], HTTPException]:
    try:
        # Valider le niveau
        if not validate_log_level(level):
            return Err(
                HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid log level"
                )
            )

        # Vérifier si l'utilisateur a accès au projet
        project_result = check_project_ownership(project_id, user_id, db)
        if project_result.is_err():
            return Err(project_result.unwrap_err())

        logs = (
            db.query(Log)
            .filter(Log.project_id == project_id, Log.level == level.lower())
            .order_by(Log.created_at.desc())
            .all()
        )

        return Ok(logs)

    except Exception as e:
        return Err(
            HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred",
            )
        )


def get_logs_by_category(
    project_id: str, category: str, user_id: str, db: Session
) -> Result[List[Log], HTTPException]:
    try:
        # Vérifier si l'utilisateur a accès au projet
        project_result = check_project_ownership(project_id, user_id, db)
        if project_result.is_err():
            return Err(project_result.unwrap_err())

        logs = (
            db.query(Log)
            .filter(Log.project_id == project_id, Log.category == category)
            .order_by(Log.created_at.desc())
            .all()
        )

        return Ok(logs)

    except Exception as e:
        return Err(
            HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred",
            )
        )


def get_logs_by_tag(
    project_id: str, tag: str, user_id: str, db: Session
) -> Result[List[Log], HTTPException]:
    try:
        # Vérifier si l'utilisateur a accès au projet
        project_result = check_project_ownership(project_id, user_id, db)
        if project_result.is_err():
            return Err(project_result.unwrap_err())

        from sqlalchemy import or_

        logs = (
            db.query(Log)
            .filter(Log.project_id == project_id)
            .filter(Log.tags.op("?")(tag))
            .order_by(Log.created_at.desc())
            .all()
        )

        return Ok(logs)

    except Exception as e:
        return Err(
            HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred",
            )
        )
