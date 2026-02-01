from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_permissions
from app.api.v1.routes_auth import get_current_user
from app.core.acl import PERMISSIONS
from app.db.session import get_db
from app.models.role import Role
from app.models.user import User
from app.schemas.role import RoleCreate, RoleRead


router = APIRouter()


@router.get("/acls", response_model=List[str])
def list_acls(
    current_user: User = Depends(get_current_user),
    _perms=Depends(require_permissions("all", "system.admin")),
):
    """List all available ACL (permission) codes defined in the system."""
    return sorted(PERMISSIONS)


@router.get("/", response_model=List[RoleRead])
def list_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _perms=Depends(require_permissions("all", "system.admin")),
):
    return db.query(Role).all()


@router.get("/{role_id}", response_model=RoleRead)
def get_role(
    role_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _perms=Depends(require_permissions("all", "system.admin")),
):
    role = db.get(Role, role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return role


@router.post("/", response_model=RoleRead, status_code=status.HTTP_201_CREATED)
def create_role(
    payload: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _perms=Depends(require_permissions("all", "system.admin")),
):
    existing = db.query(Role).filter(Role.name == payload.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role name already exists",
        )
    role = Role(
        name=payload.name,
        description=payload.description,
        permissions=payload.permissions or [],
        is_system=payload.is_system,
    )
    db.add(role)
    db.commit()
    db.refresh(role)
    return role
