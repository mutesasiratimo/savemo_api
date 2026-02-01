from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_permissions
from app.api.v1.routes_auth import get_current_user
from app.db.session import get_db
from app.models.group import Group
from app.models.user import User
from app.schemas import GroupCreate, GroupRead


router = APIRouter()


@router.post("/", response_model=GroupRead, status_code=status.HTTP_201_CREATED)
def create_group(
    payload: GroupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _perms=Depends(require_permissions("all", "system.admin", "group.manage_members")),
):
    group = Group(
        name=payload.name,
        code=payload.code,
        description=payload.description,
        parent_group_id=payload.parent_group_id,
    )
    db.add(group)
    db.commit()
    db.refresh(group)
    return group


@router.get("/", response_model=List[GroupRead])
def list_groups(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _perms=Depends(require_permissions("all", "system.admin", "group.view", "group.manage_members")),
):
    groups = db.query(Group).all()
    return groups


@router.get("/{group_id}", response_model=GroupRead)
def get_group(
    group_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _perms=Depends(require_permissions("all", "system.admin", "group.view", "group.manage_members")),
):
    group = db.get(Group, group_id)
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    return group

