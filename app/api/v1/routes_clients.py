from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_permissions
from app.api.v1.routes_auth import get_current_user
from app.db.session import get_db
from app.models.client import Client
from app.models.group import Group, GroupMembership
from app.models.user import User
from app.schemas import ClientCreate, ClientRead


router = APIRouter()


@router.post("/", response_model=ClientRead, status_code=status.HTTP_201_CREATED)
def create_client(
    payload: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _perms=Depends(require_permissions("all", "system.admin")),
):
    """
    Create a new client (tenant/organization).

    Side effects:
    - Create a default savings group for the client.
    - Add the onboarding user as the first member of that group.
    """
    # Create default group
    group = Group(
        name=f"{payload.name} Main Group",
        description=payload.tagline,
    )
    db.add(group)
    db.flush()  # get group.id

    # Add onboarding user as first member
    membership = GroupMembership(user_id=current_user.id, group_id=group.id)
    db.add(membership)

    # Create client record
    client = Client(
        name=payload.name,
        tagline=payload.tagline,
        primary_color=payload.primary_color,
        secondary_color=payload.secondary_color,
        default_group_id=group.id,
    )
    db.add(client)

    db.commit()
    db.refresh(client)
    return client


@router.get("/", response_model=List[ClientRead])
def list_clients(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _perms=Depends(require_permissions("all", "system.admin")),
):
    clients = db.query(Client).all()
    return clients

