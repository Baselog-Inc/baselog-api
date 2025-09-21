from collections.abc import Sequence
from sqlalchemy.orm import Session
from typing import List, Optional
from src.models.base import get_db
from src.models.project import Project
from src.models.user import User
from src.utils.result import Result, Ok, Err
from fastapi import HTTPException, status


def create_project(
    project_data: dict, db: Session, owner: User
) -> Result[Project, HTTPException]:
    try:
        if not is_project_name_available(project_data["name"], str(owner.id), db):
            return Err(
                HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Project name already exists for this user",
                )
            )

        new_project = Project(name=project_data["name"], owner_id=owner.id)

        db.add(new_project)
        db.commit()
        db.refresh(new_project)

        return Ok(new_project)

    except Exception as e:
        return Err(
            HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create project",
            )
        )


def get_projects_by_user(
    user_id: str, db: Session
) -> Result[Sequence[Project], HTTPException]:
    try:
        projects = (
            db.query(Project)
            .filter(Project.owner_id == user_id)
            .order_by(Project.created_at.desc())
            .all()
        )

        return Ok(projects)

    except Exception as e:
        return Err(
            HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred",
            )
        )


def get_user_project(
    project_id: str, user_id: str, db: Session
) -> Result[Project, HTTPException]:
    try:
        project = (
            db.query(Project)
            .filter(Project.id == project_id, Project.owner_id == user_id)
            .first()
        )

        if project is None:
            return Err(
                HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found or access denied",
                )
            )

        return Ok(project)

    except Exception as e:
        return Err(
            HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred",
            )
        )


def update_project(
    project_id: str, project_data: dict, user_id: str, db: Session
) -> Result[Project, HTTPException]:
    """Mettre à jour un projet avec vérification ownership"""
    try:
        # Vérifier si l'utilisateur est propriétaire du projet
        ownership_check = check_project_ownership(project_id, user_id, db)
        if ownership_check.is_err():
            return Err(ownership_check.unwrap_err())

        # Vérifier si le nouveau nom est disponible (si un nouveau nom est fourni)
        if (
            "name" in project_data
            and project_data["name"] != ownership_check.unwrap().name
        ):
            if not is_project_name_available(
                project_data["name"], user_id, db, exclude_id=project_id
            ):
                return Err(
                    HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Project name already exists for this user",
                    )
                )

        # Récupérer le projet à mettre à jour
        project_result = get_user_project(project_id, user_id, db)
        if project_result.is_err():
            return Err(project_result.unwrap_err())

        project = project_result.unwrap()

        # Mettre à jour les champs
        if "name" in project_data:
            project.name = project_data["name"]

        db.commit()
        db.refresh(project)

        return Ok(project)

    except Exception as e:
        return Err(
            HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update project",
            )
        )


def delete_project(
    project_id: str, user_id: str, db: Session
) -> Result[bool, HTTPException]:
    """Supprimer un projet avec vérification ownership"""
    try:
        # Vérifier si l'utilisateur est propriétaire du projet
        ownership_check = check_project_ownership(project_id, user_id, db)
        if ownership_check.is_err():
            return Err(ownership_check.unwrap_err())

        # Récupérer le projet à supprimer
        project_result = get_user_project(project_id, user_id, db)
        if project_result.is_err():
            return Err(project_result.unwrap_err())

        project = project_result.unwrap()

        # Supprimer le projet
        db.delete(project)
        db.commit()

        return Ok(True)

    except Exception as e:
        return Err(
            HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete project",
            )
        )


def check_project_ownership(
    project_id: str, user_id: str, db: Session
) -> Result[bool, HTTPException]:
    try:
        project = (
            db.query(Project)
            .filter(Project.id == project_id, Project.owner_id == user_id)
            .first()
        )

        if project is None:
            return Err(
                HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found or access denied",
                )
            )

        return Ok(True)

    except Exception as e:
        return Err(
            HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred",
            )
        )


def is_project_name_available(
    name: str, user_id: str, db: Session, exclude_id: Optional[str] = None
) -> bool:
    try:
        query = db.query(Project).filter(
            Project.name == name, Project.owner_id == user_id
        )

        if exclude_id:
            query = query.filter(Project.id != exclude_id)

        existing_project = query.first()
        return existing_project is None

    except Exception:
        return False
